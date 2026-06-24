import base64
import logging
import os
import shutil
import uuid

from competitions.models import Entry, File
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.views import APIView

from .parsers import TusUploadParser
from .signals import tus_upload_finished_signal

logger = logging.getLogger(__name__)


TUS_HEADERS = [
    OpenApiParameter(
        name="Tus-Resumable",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        required=True,
        description="TUS protocol version (must be 1.0.0).",
    ),
    OpenApiParameter(
        name="Upload-Metadata",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        description="Comma-separated key-value pairs of base64-encoded upload metadata (e.g. filename, filetype).",
    ),
]

RESOURCE_ID_PARAM = OpenApiParameter(
    name="resource_id",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description="UUID of the upload resource.",
)

TUS_RESPONSE_HEADERS = {
    "Tus-Resumable": {"schema": {"type": "string"}, "description": "TUS protocol version."},
    "Tus-Version": {"schema": {"type": "string"}, "description": "Supported TUS versions."},
    "Tus-Extension": {"schema": {"type": "string"}, "description": "Supported TUS extensions."},
    "Tus-Max-Size": {"schema": {"type": "integer"}, "description": "Maximum upload size in bytes."},
}


class TusUpload(APIView):
    parser_classes = (TusUploadParser,)

    queryset = File.objects.none()

    TUS_UPLOAD_URL = getattr(settings, "TUS_UPLOAD_URL", "/media")
    TUS_UPLOAD_DIR = getattr(settings, "TUS_UPLOAD_DIR", os.path.join(settings.BASE_DIR, "tmp/uploads/"))
    TUS_DESTINATION_DIR = getattr(settings, "TUS_DESTINATION_DIR", settings.MEDIA_ROOT)
    TUS_MAX_FILE_SIZE = getattr(settings, "TUS_MAX_FILE_SIZE", 4294967296)  # in bytes
    TUS_FILE_OVERWRITE = getattr(settings, "TUS_FILE_OVERWRITE", True)
    TUS_TIMEOUT = getattr(settings, "TUS_TIMEOUT", 3600)

    tus_api_version = "1.0.0"
    tus_api_version_supported = ["1.0.0"]
    tus_api_extensions = ["creation", "termination", "file-check"]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        # Support X-HTTP-Method-Override for clients behind restrictive proxies
        override_method = self.request.META.get("HTTP_X_HTTP_METHOD_OVERRIDE", None)
        if override_method:
            self.request.method = override_method

        return super().dispatch(*args, **kwargs)

    def get_tus_response(self):
        response = HttpResponse()
        response["Tus-Resumable"] = self.tus_api_version
        response["Tus-Version"] = ",".join(self.tus_api_version_supported)
        response["Tus-Extension"] = ",".join(self.tus_api_extensions)
        response["Tus-Max-Size"] = self.TUS_MAX_FILE_SIZE
        response["Cache-Control"] = "no-store"

        return response

    @extend_schema(
        operation_id="tus_file_check",
        summary="Check if a file already exists",
        description="Checks whether a file with the given name has already been uploaded.",
        parameters=TUS_HEADERS,
        responses={
            200: OpenApiResponse(
                description="File existence check result.",
                response=OpenApiTypes.NONE,
            ),
            405: OpenApiResponse(description="Missing Tus-Resumable header."),
        },
    )
    def get(self, request, *args, **kwargs):
        metadata = {}
        response = self.get_tus_response()

        if request.META.get("HTTP_TUS_RESUMABLE", None) is None:
            return HttpResponse(status=405, content="Method Not Allowed")

        for kv in request.META.get("HTTP_UPLOAD_METADATA", None).split(","):
            key, value = kv.split(" ")
            metadata[key] = base64.b64decode(value)

        if metadata.get("filename", None) and metadata.get("filename").upper() in [
            f.upper() for f in os.listdir(os.path.dirname(self.TUS_UPLOAD_DIR))
        ]:
            response["Tus-File-Name"] = metadata.get("filename")
            response["Tus-File-Exists"] = True
        else:
            response["Tus-File-Exists"] = False
        return response

    @extend_schema(
        operation_id="tus_options",
        summary="TUS server capabilities",
        description="Returns the TUS protocol capabilities and configuration of this server.",
        responses={
            204: OpenApiResponse(description="Server capabilities returned in headers."),
        },
    )
    def options(self, request, *args, **kwargs):
        response = self.get_tus_response()
        response.status_code = 204
        return response

    def _parse_upload_metadata(self, request):
        metadata = {}

        message_id = request.META.get("HTTP_MESSAGE_ID", None)
        if message_id:
            metadata["message_id"] = base64.b64decode(message_id)

        upload_metadata = request.META.get("HTTP_UPLOAD_METADATA", None)
        if upload_metadata:
            for kv in upload_metadata.split(","):
                if " " in kv:
                    key, value = kv.split(" ")
                else:
                    key = kv
                    value = ""
                metadata[key] = base64.b64decode(value).decode("utf-8")

        return metadata

    def _check_file_overwrite(self, filename):
        if self.TUS_FILE_OVERWRITE or not filename:
            return False
        try:
            return os.path.lexists(os.path.join(self.TUS_UPLOAD_DIR, filename))
        except OSError:
            sanitized = str(filename).replace("\n", "\\n").replace("\r", "\\r")
            logger.error("Unable to access file: %s", sanitized)
            return False

    def _store_upload_cache(self, resource_id, metadata, file_size, entry_id, file_type):
        cache.add(f"tus-uploads/{resource_id}/filename", metadata.get("filename"), self.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/file_size", file_size, self.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/offset", 0, self.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/metadata", metadata, self.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/type", file_type, self.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/entry", entry_id, self.TUS_TIMEOUT)

    def _create_upload_file(self, resource_id, file_size):
        with os.fdopen(os.open(os.path.join(self.TUS_UPLOAD_DIR, resource_id), os.O_WRONLY | os.O_CREAT), "wb") as f:
            f.seek(file_size)
            f.write(b"\0")

    @extend_schema(
        operation_id="tus_create_upload",
        summary="Create a new upload resource",
        description=(
            "Creates a new TUS upload resource. Returns a Location header with the URL "
            "to use for uploading chunks via PATCH."
        ),
        parameters=[
            *TUS_HEADERS,
            OpenApiParameter(
                name="Upload-Length",
                type=OpenApiTypes.INT64,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Total size of the file in bytes.",
            ),
            OpenApiParameter(
                name="X-Unicorn-Entry-Id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.HEADER,
                required=True,
                description="ID of the competition entry this upload belongs to.",
            ),
            OpenApiParameter(
                name="X-Unicorn-File-Type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                description="Type of file being uploaded (e.g. screenshot, entry).",
            ),
        ],
        request=None,
        responses={
            201: OpenApiResponse(description="Upload resource created. Location header contains the upload URL."),
            400: OpenApiResponse(description="No matching entry for the provided entry ID."),
            409: OpenApiResponse(description="File already exists and overwriting is disabled."),
            500: OpenApiResponse(description="Unsupported protocol or server error."),
        },
    )
    def post(self, request, *args, **kwargs):
        response = self.get_tus_response()

        if request.META.get("HTTP_TUS_RESUMABLE", None) is None:
            logger.warning("Received File upload for unsupported file transfer protocol")
            response.status_code = 500
            response.reason_phrase = "Received File upload for unsupported file transfer protocol"
            return response

        metadata = self._parse_upload_metadata(request)

        if self._check_file_overwrite(metadata.get("filename")):
            response.status_code = 409
            return response

        try:
            entry_id = request.META.get("HTTP_X_UNICORN_ENTRY_ID")
            entry = Entry.objects.get(pk=entry_id)
        except ObjectDoesNotExist:
            response.status_code = 400
            response.reason_phrase = "No matching entry for this upload"
            return response

        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))
        resource_id = str(uuid.uuid4())

        try:
            self._create_upload_file(resource_id, file_size)
        except IOError as e:
            logger.error(
                "Unable to create file: %s",
                str(e).replace("\n", "\\n").replace("\r", "\\r"),
                exc_info=True,
            )
            response.status_code = 500
            return response

        self._store_upload_cache(
            resource_id, metadata, file_size, entry.pk, request.META.get("HTTP_X_UNICORN_FILE_TYPE")
        )

        response.status_code = 201
        response["Location"] = f"{request.build_absolute_uri()}{resource_id}"
        return response

    @extend_schema(
        operation_id="tus_upload_offset",
        summary="Get the current upload offset",
        description="Returns the current offset for a resumable upload, used to resume interrupted transfers.",
        parameters=[RESOURCE_ID_PARAM, *TUS_HEADERS],
        responses={
            200: OpenApiResponse(description="Current upload offset and total length returned in headers."),
            404: OpenApiResponse(description="Upload resource not found."),
        },
    )
    def head(self, request, *args, **kwargs):
        response = self.get_tus_response()
        resource_id = kwargs.get("resource_id", None)

        offset = cache.get(f"tus-uploads/{resource_id}/offset")
        file_size = cache.get(f"tus-uploads/{resource_id}/file_size")
        if offset is None:
            response.status_code = 404
            return response

        else:
            response.status_code = 200
            response["Upload-Offset"] = offset
            response["Upload-Length"] = file_size

        return response

    @extend_schema(
        operation_id="tus_upload_chunk",
        summary="Upload a file chunk",
        description=(
            "Uploads a chunk of the file at the given offset. " "When all bytes are received the file is finalized."
        ),
        parameters=[
            RESOURCE_ID_PARAM,
            *TUS_HEADERS,
            OpenApiParameter(
                name="Upload-Offset",
                type=OpenApiTypes.INT64,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Byte offset within the upload where this chunk starts.",
            ),
            OpenApiParameter(
                name="Content-Length",
                type=OpenApiTypes.INT64,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Size of the chunk being uploaded in bytes.",
            ),
        ],
        request={"application/offset+octet-stream": OpenApiTypes.BINARY},
        responses={
            200: OpenApiResponse(description="Chunk uploaded. Upload-Offset header reflects the new offset."),
            400: OpenApiResponse(description="Invalid resource ID."),
            409: OpenApiResponse(description="Offset mismatch — client and server are out of sync."),
            410: OpenApiResponse(description="Upload resource no longer exists."),
            500: OpenApiResponse(description="Server error writing chunk."),
        },
    )
    def patch(self, request, *args, **kwargs):
        response = self.get_tus_response()

        resource_id = kwargs.get("resource_id", None)

        # Validate resource_id is a valid UUID to prevent path traversal
        try:
            uuid.UUID(resource_id)
        except (ValueError, AttributeError, TypeError):
            response.status_code = 400
            return response

        filename = cache.get(f"tus-uploads/{resource_id}/filename")
        file_size = int(cache.get(f"tus-uploads/{resource_id}/file_size") or 0)
        metadata = cache.get(f"tus-uploads/{resource_id}/metadata")
        offset = cache.get(f"tus-uploads/{resource_id}/offset")
        entry_id = cache.get(f"tus-uploads/{resource_id}/entry")
        entry_filetype = cache.get(f"tus-uploads/{resource_id}/type")

        file_offset = int(request.META.get("HTTP_UPLOAD_OFFSET", 0))
        chunk_size = int(request.META.get("CONTENT_LENGTH", 102400))

        upload_file_path = os.path.join(self.TUS_UPLOAD_DIR, resource_id)
        if filename is None or os.path.lexists(upload_file_path) is False:
            response.status_code = 410
            return response

        if file_offset != offset:  # check to make sure we're in sync
            response.status_code = 409  # HTTP 409 Conflict
            return response

        try:
            flags = os.O_RDWR
            mode = "r+b"
            if not os.path.exists(upload_file_path):
                flags |= os.O_CREAT
                mode = "wb"
            with os.fdopen(os.open(upload_file_path, flags), mode) as f:
                f.seek(file_offset)
                f.write(request.body)
        except IOError as e:
            logger.error("Unable to write chunk: %s", e, exc_info=True)
            response.status_code = 500
            return response

        new_offset = cache.incr(f"tus-uploads/{resource_id}/offset", chunk_size)
        response["Upload-Offset"] = new_offset

        if file_size == new_offset:  # file transfer complete, rename from resource id to actual filename
            filename = f"{uuid.uuid4().hex}_{os.path.basename(filename)}"
            shutil.move(upload_file_path, os.path.join(self.TUS_DESTINATION_DIR, filename))
            cache.delete_many(
                [
                    f"tus-uploads/{resource_id}/file_size",
                    f"tus-uploads/{resource_id}/filename",
                    f"tus-uploads/{resource_id}/offset",
                    f"tus-uploads/{resource_id}/metadata",
                    f"tus-uploads/{resource_id}/entry",
                    f"tus-uploads/{resource_id}/type",
                ]
            )
            tus_upload_finished_signal.send(
                sender=self.__class__,
                metadata=metadata,
                filename=filename,
                upload_file_path=upload_file_path,
                file_size=file_size,
                upload_url=self.TUS_UPLOAD_URL,
                destination_folder=self.TUS_DESTINATION_DIR,
                entry_id=entry_id,
                uploader=request.user.id,
                type=entry_filetype,
            )

        return response
