from oneloginapi import APIObject, OneLogin, API_HOST


class Role(APIObject):
    """ A OneLogin Role object

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """
    _url = "%s/api/v1/roles" % API_HOST
    def __init__(self, el=None, id_=None, api_key=None):
        self._url = "%s/%s.xml" % (self._url, id_)
        super(Role, self).__init__(el=el, id_=id_, api_key=api_key)


class Roles(OneLogin):
    """ OneLogin API for Roles

    See also https://developers.onelogin.com/v1.0/docs/get-all-roles
    """

    _url = "%s/api/v1/roles.xml" % API_HOST

    def __init__(self, api_key):
        super(Roles, self).__init__(api_key)

    def list(self, refresh=False):
        # pylint: disable=no-member
        return self._list(api_type="role", cls=Role, refresh=refresh)
