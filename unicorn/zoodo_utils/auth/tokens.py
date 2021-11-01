import datetime

from oauthlib.common import to_unicode


def generate_signed_token(private_pem, request):
    import jwt

    now = datetime.datetime.utcnow()

    claims = {
        'iss': now,
        'exp': now + datetime.timedelta(seconds=request.expires_in)
    }

    claims.update(request.claims)

    token = jwt.encode(claims, private_pem, 'RS256')
    token = to_unicode(token, "UTF-8")

    return token


def signed_token_generator(private_pem, **kwargs):
    def signed_token_generator(request):
        request.claims = {
            'uid': request.user.pk,
            'email': request.user.email,
            'username': request.user.username,
            'first_name': request.user.profile.first_name,
            'last_name': request.user.profile.last_name,
            'display_name': request.user.profile.display_name,
            **kwargs,
        }

        return generate_signed_token(private_pem, request)

    return signed_token_generator
