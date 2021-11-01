import requests
from django.core.cache import cache


class ToornamentBase(object):
    """
    Toornament API Base class
    """

    api_key = "23tDgZuK8SJefQSPvHrckkGWn0TsOD1ZiH5GCgGabrI"
    client_id = (
        "589749b1150ba02e3d8b456753b3cismgsg0wo0scckc0kkww4844k88w0sc0gosc0sw0w0oko"
    )
    client_secret = "3exfy4j36a80wokc08c80w4kc8kscksw0gg0owo8ws8go84o4g"

    base_url = "https://api.toornament.com/organizer/v2/"

    def get_bearer_token(self, scopes=None):
        """
        Using the class parameters `client_id` and `client_secret`,
        get the bearer token to use in future requests towards the API.
        :param scopes: list
        :return: None|string
        """
        # define default scope list if none were explicitly requested
        if not scopes:
            scopes = [
                "organizer:view",
                "organizer:result",
                "organizer:participant",
                "organizer:registration",
            ]

        # try to fetch token from cache first
        cached = cache.get("toornament/bearer-token")
        if cached:
            return cached

        # build and send request
        url = "https://api.toornament.com/oauth/v2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": " ".join(scopes),
        }
        response = requests.post(url, data=data)

        # blank response for non-200 responses
        if response.status_code != 200:
            return None

        # cache token for later use before we hand it over
        data = response.json()
        cache.add("toornament/bearer-token", data["access_token"], data["expires_in"])
        return data["access_token"]

    def get_api_headers(self, headers=None):
        """
        Generate a dict with all headers to be attached to the request
        by merging additional request-specific headers into the default
        headers always present.
        :param headers: dict
        :return: dict
        """
        # these are our standard headers
        header_data = {
            "X-Api-Key": self.api_key,
            "Authorization": "Bearer " + self.get_bearer_token(),
            "Content-Type": "application/json",
        }

        # merge with custom headers if they are present
        if headers:
            return {**header_data, **headers}

        # .. or just send default headers
        return header_data

    def api_get(self, endpoint, headers=None):
        """
        Execute a GET request
        :param endpoint: string
        :param headers: dict
        :return: :class:`Response <Response>` object
        """
        return requests.get(
            self.base_url + endpoint, headers=self.get_api_headers(headers)
        )

    def api_post(self, endpoint, data, headers=None):
        """
        Execute a POST request
        :param endpoint: string
        :param data: dict
        :param headers: dict
        :return: :class:`Response <Response>` object
        """
        return requests.post(
            self.base_url + endpoint, headers=self.get_api_headers(headers), json=data
        )

    def api_put(self, endpoint, data, headers=None):
        """
        Execute a PUT request
        :param endpoint: string
        :param data: dict
        :param headers: dict
        :return: :class:`Response <Response>` object
        """
        return requests.put(
            self.base_url + endpoint, headers=self.get_api_headers(headers), json=data
        )

    def api_patch(self, endpoint, data, headers=None):
        """
        Execute a PATCH request
        :param endpoint: string
        :param data: dict
        :param headers: dict
        :return: :class:`Response <Response>` object
        """
        return requests.patch(
            self.base_url + endpoint, headers=self.get_api_headers(headers), json=data
        )

    def api_delete(self, endpoint, headers=None):
        """
        Execute a DELETE request
        :param endpoint: string
        :param headers: dict
        :return: :class:`Response <Response>` object
        """
        return requests.delete(
            self.base_url + endpoint, headers=self.get_api_headers(headers)
        )


class Tournament(ToornamentBase):
    """
    Class for interacting with Toornament Tournaments.
    """

    def __init__(self):
        self.obj = None

    def retrieve(self, id):
        """
        Retrieve a specific Tournament based on ID.
        :param id: string
        :return: dict
        """
        r = self.api_get("tournaments/{}".format(id))

        if r.status_code != 200:
            return None

        self.obj = r.json()
        return self.obj

    def add_participant(self, data):
        """
        Add a participant to the Tournament, either
        single player or team, using data from the Entry.
        :param data: dict
        :return: string
        """
        if not self.obj:
            raise ValueError("Can't add participants without a Tournament ID")

        if data.get("id"):
            r = self.api_patch(
                "tournaments/{}/participants/{}".format(self.obj["id"], data["id"]),
                data=data,
            )

            if r.status_code != 200:
                return None
        else:
            r = self.api_post(
                "tournaments/{}/participants".format(self.obj["id"]), data=data
            )

            if r.status_code != 201:
                return None

        return r.json()["id"]


class Match(ToornamentBase):
    """
    Class for interacting with Toornament Matches
    """

    def __init__(self):
        self.obj = None

    def retrieve(self, compo_id, match_id):
        """
        Retrieve a specific Match based on ID.
        :param compo_id: string
        :param match_id: string
        :return: dict
        """
        r = self.api_get("tournaments/{}/matches/{}".format(compo_id, match_id))

        if r.status_code != 200:
            return None

        self.obj = r.json()
        return self.obj

    def find_by_participant(self, compo_id, participant_id):
        """
        Retrieve matches based on searching for a participant ID
        :param compo_id: string
        :param participant_id: string
        :return: dict
        """
        r = self.api_get(
            "tournaments/{}/matches?participant_ids={}".format(
                compo_id, participant_id
            ),
            headers={"Range": "matches=0-99"},
        )

        if r.status_code != 206:
            return None

        data = r.json()

        # we need to append the participant data for pretty display in the front-end
        for num, match in enumerate(data):
            for idx, plebs in enumerate(match["opponents"]):
                r = self.api_get(
                    "tournaments/{}/participants/{}".format(
                        compo_id, plebs["participant"]["id"]
                    )
                )

                if r.status_code != 200:
                    continue

                participant = r.json()
                participant.pop("email")
                for player in participant["lineup"]:
                    player.pop("email")

                data[num]["opponents"][idx]["participant"] = participant

        return data
