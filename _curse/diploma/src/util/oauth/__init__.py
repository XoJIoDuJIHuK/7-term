from src.settings import OAuthProvider
from src.util.oauth.google import GoogleOAuth2Authorize


oauth_provider_classes = {
    OAuthProvider.google.value: GoogleOAuth2Authorize,
}
