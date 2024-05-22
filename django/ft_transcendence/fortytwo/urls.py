from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import FortytwoProvider

urlpatterns = default_urlpatterns(FortytwoProvider)

