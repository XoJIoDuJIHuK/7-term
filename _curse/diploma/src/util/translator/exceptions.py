class TranslatorError(Exception):
    """Base error"""
    pass


class TranslatorConfigInvalid(TranslatorError):
    pass


class TranslatorAPIError(TranslatorError):
    pass


class TranslatorTextTooLongError(TranslatorError):
    pass


class TranslatorAPITimeoutError(TranslatorError):
    pass
