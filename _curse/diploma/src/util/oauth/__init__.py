from src.settings import OAuthProvider
from src.util.oauth.google import GoogleOAuth2Authorize
from src.util.oauth.mail import MailOAuth2Authorize
from src.util.oauth.vk import VkOAuth2Authorize
from src.util.oauth.yandex import YandexOAuth2Authorize


oauth_provider_classes = {
    OAuthProvider.google.value: GoogleOAuth2Authorize,
    OAuthProvider.mail_ru.value: MailOAuth2Authorize,
    OAuthProvider.yandex.value: YandexOAuth2Authorize,
    OAuthProvider.vk.value: VkOAuth2Authorize,
}
