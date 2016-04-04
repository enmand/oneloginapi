import logging
import lxml.etree
import lxml.objectify
import requests

from oneloginapi.exceptions import APIObjectException

API_HOST = "https://api.onelogin.com"
API_VERS = "/api/v3"
API_URL = "%s%s" % (API_HOST, API_VERS)


class OneLogin(object):
    """ OneLogin base class for common API management """

    # The URL for this OneLogin API target
    _url   = None

    # The XML cache of the OneLogin API target (for some operations)
    _cache = None


    def __init__(self, api_key):
        """ Initialize the OneLogin API, with the given API key

        Parameters:
            api_key - The API key to use when interacting with OneLogin. See
                http://developers.onelogin.com/v1.0/docs#section-get-an-api-key
        """
        # cache for calls that require listing for identification
        self._api_key = api_key
        self._conn = OneLogin.session(api_key)

        self.l = logging.getLogger(str(OneLogin.__class__))


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

    def _list(self, api_type, cls, refresh=False):
        """ Return a full list of the object represented by this APIObject.

        Parameters:
            api_type - The APIObject type to list
            refresh  - If we should reload fresh user information from the
                       OneLogin server
        Returns:
            lxml.etree.Element
        """
        resp = self._reload(self._url)

        objlist = getattr(resp, api_type)

        return [cls(id_=o.id, api_key=self._api_key) for o in objlist]


    def _filter(self, api_type, cls, search, field):
        """ Filter objects on OneLogin by some field for this APIObject type

        Parameters:
            api_type - The APIObject type to list
            search - The search term to use
            field  - The field to search on
        Return:
            [User, ...]
        """
        self.l.debug("filter (field %s): %s", field, search)

        resp = self._reload(self._url, {"page": "1"}, paged=True)

        results = resp.xpath('//%s/%s[text()="%s"]/..' % (
            api_type, field, search,
        ))

        xp = [cls(id_=el.id, api_key=self._api_key) for el in results]
        return xp


    def _find(self, api_type, cls, search, field):
        """ Find a single user, based on your search

        This function will return a single user, who is the first user to match
        the given search criteria

        Parameters:
            api_type - The APIObject type to list
            cls      - The class to use when instantiating in our filter
            search   - The search term to use
            field    - The field to search on
        Return:
            Users
        """
        apobj = self._filter(api_type, cls, search, field)

        if len(apobj) > 0:
            return apobj[0]

        return None


    def _reload(self, url=None, data=None, paged=False):
        """ Reload OneLogin users from the OneLogin server """
        self.l.debug("reloading cache from %s", url)
        if url == None:
            url = self._url

        resp = self._conn.get(url, params=data)
        # pylint: disable=no-member
        elem = lxml.objectify.fromstring(resp.content)

        if paged:
            if elem.tag == 'nil-classes':
                return None
            else:
                data["page"] = int(data["page"]) + 1
                next_page = self._reload(url, data, paged)
                if next_page is not None:
                    elem.extend(next_page)

        return elem

class APIObject(object):
    """ A OneLogin API object

    See also http://developers.onelogin.com
    """

    # API Key to use to interact with OneLOgin
    _api_key   = None

    # URL for this APIObject
    _url      = None

    # (XML) detail representation of this object from OneLogin
    __details = None

    def __init__(self, el=None, id_=None, api_key=None):
        name = str(self.__class__)
        self.l = logging.getLogger(name)
        self._api_key = api_key

        if api_key is None:
            raise APIObjectException("You must pass an API Key to use")

        if (el is None and id_ is None) or (el is not None and id_ is not None):
            raise APIObjectException(
                "You must pass either XML, or the ID to load"
            )

        if el is not None:
            self.__details = el

        if id_ is not None and self._url is not None:
            resp = OneLogin.session(api_key).get(self._url)
            # pylint: disable=no-member
            self.__details = lxml.objectify.fromstring(resp.content)

        if self.__details is None:
            if id_ and not self._url:
                raise APIObjectException(
                    "Could not load details: id_ given with no object _url"
                )

            raise APIObjectException(
                "Could not load detials"
            )

        self._id = self._find("id")
        if self._id is not None:
            self._id = self._id.text  # pylint: disable=no-member
        else:
            raise APIObjectException("Invalid API Object ID given: %s", id_)
        self.l.info("Loaded %s %s", name, self._id)

    def __getattr__(self, key):
        f = self._find(key)
        if f is None:
            return None
        self.l.debug("getattr %s (for %s): %s", key, self._id, f.text)

        return f.text

    def _find(self, key):
        return self.__details.find(key)
