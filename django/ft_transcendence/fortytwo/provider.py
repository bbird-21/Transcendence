from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from .views import FortytwoOAuth2Adapter


class FortytwoAccount(ProviderAccount):
    pass


class FortytwoProvider(OAuth2Provider):

    id = 'fortytwo'
    name = 'Fortytwo'
    account_class = FortytwoAccount
    oauth2_adapter_class = FortytwoOAuth2Adapter

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    displayname=data["displayname"],
                )

    def get_default_scope(self):
        return ["public"]

provider_classes = [FortytwoProvider]
