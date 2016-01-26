# pylint: disable=no-member
import logging
from hashlib import sha256

import lxml.etree
import requests

from dicttoxml import dicttoxml

from oneloginapi import (OneLogin, APIObject, API_URL,
                         API_HOST)
from oneloginapi.exceptions import NetworkException
from oneloginapi.roles import Role
from oneloginapi.apps import App


class Users(OneLogin):
    """ OneLogin API for Users.

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """

    _url = "%s/users.xml" % API_URL

    def __init__(self, api_key):
        super(Users, self).__init__(api_key)
        self.l = logging.getLogger(str(self.__class__))

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
            reqxml = self._conn.get("%s/api/v1/delegated_auth" % API_HOST,
                                    params={
                                        "api_key": self._api_key,
                                        "email": username,
                                        "password": password,
                                    }, timeout=timeout)
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            self.l.error("Failed to authenticate user")
            raise NetworkException
        else:
            self.l.info("Sent authentication request for %s", username)

        req = lxml.objectify.fromstring(reqxml.content)

        return req.authenticated, req.message

    def list(self, refresh=False):
        """ Return a full list of Users

        Parameters:
            refresh - If we should reload fresh user information from the
                      OneLogin server
        """
        return self._list(api_type="user", cls=User, refresh=refresh)

    def filter(self, search, field="email"):
        return self._filter(
            api_type="user",
            cls=User,
            search=search,
            field=field,
        )

    def find(self, search, field="email"):
        return self._find(api_type="user", cls=User, search=search, field=field)


class UserStatus(object):
    """ Constant representation of user status.

    See also: http://developers.onelogin.com/v1.0/docs/user-elements
    """
    DISABLED = 0
    ACTIVE = 1
    SUSPENDED = 2
    LOCKED = 3
    PASSWORD_EXPIRED = 4
    AWAITING_PASSOWRD_RESET = 5


class User(APIObject):
    """ A OneLogin User object

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """

    _url = "%s/users" % API_URL

    def __init__(self, el=None, id_=None, api_key=None):
        self._url = "%s/%s.xml" % (self._url, id_)
        super(User, self).__init__(el=el, id_=id_, api_key=api_key)

    def __getattr__(self, key):
        if key == "roles":
            f = self._find(key)
            return [
                Role(el=r, api_key=self._api_key) for r in f.findall("role")
            ]

        return super(User, self).__getattr__(key)

    def apps(self, embed_api_key):
        r = OneLogin.session(self._api_key)
        self.l.info("Sending apps request for %s", self.id)

        appreq = r.get("%s/client/apps/embed2" % API_HOST, params={
            "token": embed_api_key,
            "email": self.email,
        })

        appxml = lxml.etree.fromstring(appreq.content)

        user = User(id_=self.id, api_key=self._api_key)

        return [App(a, self._api_key, user) for a in appxml.findall("app")]

    def set_password(self, password, confirm, cleartext=True):
        """ Update the password on OneLogin for this user

        Paremters:
            - password:  The password to use for the user
            - confirm:   A confirmation of the password
            - cleartext: (optional, default=True) If we should use the
                         Cleartext API, or by using their pre-salt+sha256
                         API. Unfortunately, only the Cleartext API works when
                         OneLogin is configured for use with a Directory.
        """
        r = OneLogin.session(self._api_key)
        r.headers["Content-Type"] = "application/xml"

        req = {}
        url = "%s/users/%s" % (API_URL, self.id)

        if(not cleartext):
            req = {
                "user": {
                    "password": sha256(password).hexdigest(),
                    "password_confirmation": sha256(confirm).hexdigest(),
                    "password_algorithm": "salt+sha256"
                }
            }
            url += "set_password"
        else:
            req = {
                "user": {
                    "password": password,
                    "password_confirmation": confirm,
                }
             }

        self.l.info(
            "Sending password reset for %s to OneLogin (using cleartest: %s)",
            self.id, cleartext,
        )

        url += ".xml"  # Both endpoints end in .xml
        reqxml = dicttoxml(req, root=False)
        appreq = r.put(url, data=reqxml)

        if appreq.status_code != 200:
            respxml = lxml.etree.fromstring(appreq.content)
            err = respxml.find("message").text

            raise UserPasswordException(
                "Could not set password for %s (%s): %s" % (
                    self.username, self.email, err,
                )
            )

        return True

class UserPasswordException(Exception):
    pass
