import logging
import requests

API_HOST = "https://api.onelogin.com"
API_VERS = "/api/v3"
API_URL = "%s%s" % (API_HOST, API_VERS)


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
        self._conn = OneLogin.session(api_key)

    @staticmethod
    def session(_api_key):
        """ Create a new requests session for the OneLogin server, with the
        given API credentials.
        """
        l = logging.getLogger(str(OneLogin.__class__))
        l.info("Starting new OneLogin session with API Key: %s", _api_key)

        r = requests.Session()
        r.auth = (_api_key, "x")

        return r

class APIObject(object):
    """ A OneLogin API object

    See also http://developers.onelogin.com
    """
    def __init__(self, el):
        self.l = logging.getLogger(str(self.__class__))
        self.__details = el
        self._id = self._find("id").text

        self.l.info("Loaded %s", self._id)

    def __getattr__(self, key):
        f = self._find(key)
        if f is None:
            return None
        self.l.debug("getattr %s (for %s): %s", key, self._id, f.text)

        return f.text

    def _find(self, key):
        return self.__details.find(key)

class NetworkException(Exception):
    """ Exceptions on the network when preformation operations against OneLogin
    """
    pass
