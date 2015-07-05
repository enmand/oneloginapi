from oneloginapi import APIObject, OneLogin


class Role(APIObject):
    """ A OneLogin Role object

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """
    def __init__(self, el=None, id_=None, api_key=None):
        super(Role, self).__init__(el=el, id_=id_, api_key=api_key)


class Roles(OneLogin):
    """ OneLogin API for Roles

    See also https://developers.onelogin.com/v1.0/docs/get-all-roles
    """
    def __init__(self, api_key):
        super(Roles, self).__init__(api_key)
