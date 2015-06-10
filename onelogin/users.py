import lxml.etree
import lxml.objectify
import requests

from onelogin import (OneLogin, APIObject, API_URL,
                      API_HOST, API_VERS, NetworkException)
from onelogin.roles import Role
from onelogin.apps import App

class User(APIObject):
    """ A OneLogin User object

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """
    def __init__(self, el, api_key):
        super(User, self).__init__(el)
        self._api_key = api_key

    def __getattr__(self, key):
        f = self._find(key)

        if key == "roles":
            return map(lambda r: Role(r), f.findall("role"))

        return f.text

    def apps(self, embed_api_key):
        r = OneLogin.session(self._api_key)
        appreq = r.get("%s/client/apps/embed2" % API_HOST, params={
            "token": embed_api_key,
            "email": self.email,
        })

        appxml = lxml.etree.fromstring(appreq.content)

        return map(lambda a: App(a), appxml.findall("app"))

    @staticmethod
    def load(username, api_key):
        """ Load full information about a OneLogin user

        Load the full User information from the OneLogin server, based on
        a partial user XML (with at least the username).

        Parameters:
            el      - A <user> XML element, with at least the <username> field
            api-key - The API key to use to communicate with the OneLogin server
        """
        # Use the OneLogin API
        url = "%s/users/username/%s" % (API_URL, username)
        ureq = OneLogin.session(api_key).get(url)

        uxml = lxml.etree.fromstring(ureq.content)

        return User(uxml, api_key)

class Users(OneLogin):
    """ OneLogin API for Users.

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """
    def __init__(self, api_key):
        super(Users, self).__init__(api_key)

        self.__cache = None

    def login(self, username, password, timeout=None):
        """ Return if authentication details are correct against OneLogin.

        This does not set a cookie, or preform any session related actions for
        any web frameworks.

        Parameters:
            username - The username of the user
            password - The password to test
            timeout  - Request timeout for login

        Returns:
            boolean

        Raises:
            onelogin.NetworkException - Raises this exception if the network
                                        fails. This does not indicate if the
                                        user credentials are valid or not.
        """
        try:
            authed = self._conn.get("%s/api/v1/delegated_auth" % API_HOST, params={
            "api_key": self._api_key,
            "email": username,
            "password": password,
        }, timeout=timeout)
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
                raise NetworkException

        return authed


    def list(self, refresh=False):
        """ Return a full list of users

        Parameters:
            refresh - If we should reload fresh user information from the
                      OneLogin server
        Returns:
            lxml.etree.Element
        """
        if refresh or self.__cache is None:
            self.reload()

        return self.__cache.users

    def filter(self, search, field="email"):
        """ Filter a the users on OneLogin by some field.

        Parameters:
            search - The search term to use
            field  - The field to search on
        Return:
            [User, ...]
        """

        if self.__cache is None:
            self.reload()

        results = self.__cache.xpath('//user/%s[text()="%s"]/..' % (
            field, search,
        ))

        xp = map(lambda el: User.load(el.username, self._api_key), results)
        return xp

    def find(self, search, field="email"):
        """ Find a single user, based on your search

        This function will return a single user, who is the first user to match
        the given search criteria

        Parameters:
            search - The search term to use
            field  - The field to search on
        Return:
            Users
        """
        users = self.filter(search, field)

        if len(users) > 0:
            return users[0]

        return None

    def reload(self):
        """ Reload OneLogin users from the OneLogin server """
        url = "%s/users.xml" % API_URL
        users = self._conn.get(url)

        self.__cache = lxml.objectify.fromstring(users.content)
