import json
import requests

from oneloginapi import APIObject

from oneloginapi import API_URL


class App(APIObject):
    """ A OneLogin Role object

    See also http://developers.onelogin.com/v1.0/docs/user-elements
    """
    def __init__(self, el, api_key, user=None):
        """ Initiate a new App from OneLogin's response XML.

        Parameters:
            el      - The XML element for the App
            api_key - The API key for accessing OneLogin
            user    - (optional) The user this app should be associated with

        """
        super(App, self).__init__(el=el, api_key=api_key)
        self._user = user


    def saml_assertion(self, password, username=None):
        """ Generates a SAML assertion for this app, that can be used for SSO
        authentication with that app

        Parameters:
            - The (OneLogin) username to generate the SAML asertion for
            - The (OneLogin) password of the User for generate the SAML
            assertion for

        Returns:
            - A JSON object with a `status` and a `data` field. More information
            can be found on
            http://developers.onelogin.com/v1.0/docs/generate-saml-assertion
        """
        appreq = requests.post("%s/saml/assertion" % API_URL, data=json.dumps({
            "api_key": self._api_key,
            "username": username or self._user.email,
            "password": password,
            "app_id": int(self.id),
        }), headers={"Content-Type": "application/json"})

        return appreq.json()
