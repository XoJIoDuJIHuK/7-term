import asyncio
import re
from abc import ABC, abstractmethod
from logging import Logger

from src.database.models import Language, AIModel, StylePrompt
from src.settings import TextTranslationConfig
from src.util.translator.exceptions import TranslatorError, \
    TranslatorAPITimeoutError, TranslatorAPIError, TranslatorTextTooLongError


class AbstractTranslator(ABC):
    logger: Logger

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
            self.logger.exception(f'Ошибка API: {e}')
            raise
        except Exception as e:
            self.logger.error(f'Some error occurred: {e}.')
            raise TranslatorError(e)

    async def _process_translation(
            self,
            text: str,
            source_language: Language | None,
            target_language: Language,
            model: AIModel,
            prompt_object: StylePrompt
    ) -> str:
        """Processes the translation request

        This method handles the actual translation, including splitting text
        into chunks if necessary and storing the translation
        results in the database.

        Returns:
            str: The translated text.
        """
        try:
            if (
                    self.count_words(text) >
                    TextTranslationConfig.max_words_in_text
            ):
                raise TranslatorTextTooLongError(
                    'Превышено максимальное число слов в тексте'
                )

            prompt = prompt_object.text.format(
                source_lang=(
                    f'language with ISO code {source_language.iso_code}'
                    if source_language else 'given language'
                ),
                target_lang=f'language with ISO code '
                            f'{target_language.iso_code}'
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

            translations = await asyncio.gather(
                *(self._process_chunk(model=model, prompt=prompt, chunk=chunk)
                  for chunk in chunks)
            )

            result = ' '.join(translations)
            return result
        except ValueError:
            raise Exception('Недопустимый текст')
        except Exception as e:
            self.logger.error(e)
            raise e

    @abstractmethod
    async def _process_chunk(
            self,
            model: AIModel,
            prompt: str,
            chunk: str
    ) -> str:
        """
        This method sends prompt to specified model and returns translated
        chunk of text
        """
        pass

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
