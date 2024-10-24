import logging
import re

import google.generativeai as genai

from src.database.models import (
    Language,
    StylePrompt,
    AIModel,
)
from src.settings import LOGGER_PREFIX, TextTranslationConfig, GeminiConfig
from src.util.translator.abstract import AbstractTranslator
from src.util.translator.exceptions import (
    TranslatorAPIError,
    TranslatorAPITimeoutError,
    TranslatorError,
    TranslatorTextTooLongError,
)


class GeminiTranslator(AbstractTranslator):
    """A translator class that utilizes OpenAI's API to perform translations
    between languages.

    This class is designed to handle translation requests by constructing
    prompts dynamically and interacting with the Gemini API. It also integrates
    with a database to manage and store translation configurations and results.

    Attributes:
        logger (logging.Logger): Logger instance for logging translation
            processes.
    """

    logger = logging.getLogger(LOGGER_PREFIX + __name__)

    async def translate(
            self,
            text: str,
            source_language: Language | None,
            target_language: Language,
            model: AIModel,
            prompt_object: StylePrompt
    ) -> str:
        try:
            self.logger.info(f'Начинается перевод текста: {text}')

            result = await self._process_translation(
                text=text,
                source_language=source_language,
                target_language=target_language,
                model=model,
                prompt_object=prompt_object
            )

            self.logger.info(f'End of text translation: {result}')

            return result
        except (
            TranslatorTextTooLongError,
            TranslatorAPIError,
            TranslatorAPITimeoutError
        ) as e:
            self.logger.exception(f'Error while translating: {e}')
            raise
        except Exception as e:
            self.logger.error(f'Some error occurred: {e}.')
            raise TranslatorError(f'Some error occurred: {e}.')

    async def _process_translation(
            self,
            text: str,
            source_language: Language | None,
            target_language: Language,
            model: AIModel,
            prompt_object: StylePrompt
    ) -> str:
        """Processes the translation request using the OpenAI API.

        This method handles the actual translation, including splitting text
        into chunks if necessary and storing the translation
        results in the database.

        Returns:
            str: The translated text.
        """
        try:
            self.logger.error(f'TextTranslationConfig.max_words_in_text: {TextTranslationConfig.max_words_in_text}')
            if (
                    self.count_words(text) >
                    TextTranslationConfig.max_words_in_text
            ):
                raise TranslatorTextTooLongError(
                    'Превышено максимальное число слов в тексте'
                )

            prompt = prompt_object.text.format(
                source_lang=(
                    source_language.iso_code if source_language
                    else 'given language'
                ),
                target_lang=target_language.iso_code
            )

            chunks = [text]
            if (
                    self.count_words(text) >
                    TextTranslationConfig.max_words_in_chunk
            ):
                chunks = self.split_text_into_chunks(
                    text,
                    TextTranslationConfig.max_words_in_chunk
                )

            translations = []
            genai.configure(
                api_key=GeminiConfig.gemini_api_key
            )
            model = genai.GenerativeModel(model.name)


            for chunk in chunks:
                response = model.generate_content(prompt + " " + chunk)
                translations.append(response.text)

            result = ' '.join(translations)
            return result
        except Exception as e:
            self.logger.exception(e)
            raise e

    @staticmethod
    def count_words(text: str) -> int:
        """Counts the number of words in a given text.

        This method uses regular expressions to find and count all words in the
        text.

        Args:
            text (str): The text whose words are to be counted.

        Returns:
            int: The word count in the provided text.
        """
        match_whole_words = r'\b\w+\b'
        words = re.findall(match_whole_words, text)
        return len(words)

    def split_text_into_chunks(
            self,
            text: str,
            max_words: int
    ) -> list[str]:
        """Splits text into chunks based on a maximum word limit.

        This method splits the input text into smaller chunks by sentences,
        ensuring that each chunk does not exceed the specified maximum word
        count. The splitting is done based on sentence-ending punctuation.

        Args:
            text (str): The text to be split into chunks.
            max_words (int): The maximum number of words allowed in each chunk.

        Returns:
            list[str]: A list of text chunks, each within the word limit.
        """
        split_by_sentence_end = r'(?<=[.!?]) +'
        sentences = re.split(split_by_sentence_end, text)
        chunks = []
        current_chunk = []

        current_word_count = 0

        for sentence in sentences:
            sentence_word_count = self.count_words(sentence)

            if current_word_count + sentence_word_count > max_words:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_word_count

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
