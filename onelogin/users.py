from . import OneLogin
import lxml.objectify

API_HOST = "https://api.onelogin.com"
API_VERS = "/api/v3"
API_URL = "%s%s" % (API_HOST, API_VERS)


class Users(OneLogin):
    """ OneLogin API for Users.

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """
    def __init__(self, api_key):
        super(Users, self).__init__(api_key)

        self.__cache = None

    def login(self, username, password):
        return self._conn.get("%s/api/v1/delegated_auth" % API_HOST, params={
            "api_key": self._api_key,
            "email": username,
            "password": password,
        })

    def list(self, refresh=False):
        if refresh or self.__cache is None:
            self.__refresh()

        return self.__cache

    def filter(self, username, field="email", cached=True):
        if cached:  # Use cached version
            if self.__cache is None:
                self.__refresh()

            return self.__cache.xpath('//user/%s[text()="%s"]' % (
                field, username,
            ))
        else:
            # Use the OneLogin API
            url = "%s/users/%s" % (API_URL, username)
            return self._conn.get(url)

    def __refresh(self):
        url = "%s/users.xml" % API_URL
        users = self._conn.get(url)
        self.__cache = lxml.objectify.fromstring(users.content)
