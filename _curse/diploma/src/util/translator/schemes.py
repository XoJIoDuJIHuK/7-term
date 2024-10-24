from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from src.settings import TextTranslationConfig, GeminiConfig


class ModelConfig(BaseModel):
    """Configuration for the GPT model used in chat completions.

    This class specifies the parameters to customize the behavior of the
    GPT model for generating responses in a chat

    Attributes:
        model: The GPT model ID to use for chat completions.
        frequency_penalty: Adjusts the likelihood of generating new tokens
            based on their frequency in the text so far.
        presence_penalty: Adjusts the likelihood of generating new tokens
            based on their presence in the text so far.
        max_tokens: Limits the maximum number of tokens in the model's
            response to control the output length.
        temperature: Controls the randomness of the output.
        top_p: Controls output by only considering the top P% probability
            mass of the token distribution.
        stop: A list of strings where the model will stop generating further
            tokens. Useful for ending responses or avoiding certain topics.

    """
    model: Literal[
        'gemini',
        'gemini-flash'
    ] = 'gemini-flash'
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    max_tokens: int = Field(150, ge=0, le=4095)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop: Optional[list[str]] = Field(default=None)

    @field_validator('stop')
    @classmethod
    def validate_stop(cls, stop):
        if stop is not None and len(stop) > 4:
            raise ValueError('Stop list can have a maximum of 4 elements.')
        return stop


class TranslatorConfig(BaseModel):
    """Configuration settings for the translator.

    This class defines the configuration parameters that control the
    behavior of the translation process, including limits on the size
    of text chunks, the overall text length, and the timeout duration
    for API requests.

    Attributes:
        max_words_in_chunk (int): The maximum number of words that can be
            processed in a single chunk. This is useful for breaking down large
            texts into manageable parts. Default is 2047.

        max_words_in_text (int): The maximum number of words that can be
            processed in the entire text. This ensures the translation task
            does not exceed a certain word limit. Default is 10000.

        api_timeout (int): The timeout duration in seconds for API requests.
            This setting ensures that the translation request is terminated
            if it takes longer than the specified time. Default is 10 seconds.
    """
    max_words_in_chunk: int = Field(200)
    max_words_in_text: int = Field(10000)
    api_timeout: int = Field(15)


class GeminiTranslatorConfig(BaseModel):
    """Configuration settings for the GeminiTranslator.

    This class aggregates the configuration for the translator and the
    model, including the prompt template. It allows you to specify settings
    related to the translation process as well as the OpenAI model parameters.

    Attributes:
        translator (TranslatorConfig): The configuration settings related to
            the translator, such as word limits and API timeout.

        default_model (ModelConfig): The configuration settings for the OpenAI
            model that is used to generate translations. This includes settings
            like the model name, token limits, and other related parameters.

        default_prompt (str): The default prompt template used to initiate
            translation requests. This template can be formatted with specific
            source and target languages to customize the translation process.
            Default is an empty string.

        api_key (str): The API key used for authenticating requests to the
            OpenAI API. This key is required for accessing the translation
            service.
    """
    translator: TranslatorConfig = Field(TranslatorConfig())
    default_model: ModelConfig
    default_prompt: str = Field('')
    api_key: str | None = None

    def model_post_init(self, __context):
        self.api_key: str = GeminiConfig.gemini_api_key
