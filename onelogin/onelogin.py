import requests


class OneLogin(object):
    """ OneLogin base class for common API management """
    def __init__(self, api_key):
        """ Initialize the OneLogin API, with the given API key

        Parameters:
            api_key - The API key to use when interacting with OneLogin. See
                http://developers.onelogin.com/v1.0/docs#section-get-an-api-key
        """
        # cache for calls that require listing for identification
        self._api_key = api_key
        self._conn = requests.Session()
        self._conn.auth = (self._api_key, "x")
