from abc import ABC, abstractmethod

from src.database.models import Language, AIModel, StylePrompt


class AbstractTranslator(ABC):
    @abstractmethod
    async def translate(
            self,
            text: str,
            source_language: Language | None,
            target_language: Language,
            model: AIModel,
            prompt_object: StylePrompt
    ) -> str:
        """Asynchronously executes the translation process.

        Implement Details:
            This method should be implemented by subclasses to handle the
            translation request. It should include steps such as processing the
            input text, forming the appropriate API request, and returning the
            translated text.

        Returns:
            str: The translated text.

        Raises:
            NotImplementedError: This exception is raised if the method is not
                implemented in a subclass.
            TranslatorAPIError: Error related to the API call.
            TranslatorTextTooLongError: If the input text exceeds the maximum
                allowed length.
            TranslatorAPITimeoutError: If the translation process takes
                too long.
            TranslatorError: General error related to the translation process.
        """
        pass
