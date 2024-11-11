import logging
from urllib.parse import urljoin

import google.generativeai as genai
import requests

from src.database.models import (
    AIModel,
)
from src.settings import (
    LOGGER_PREFIX,
    GeminiConfig,
    G4FConfig,
)
from src.util.translator.abstract import AbstractTranslator


class GeminiTranslator(AbstractTranslator):
    logger = logging.getLogger(LOGGER_PREFIX + __name__)

    async def _process_chunk(
            self,
            model: AIModel,
            prompt: str,
            chunk: str
    ) -> str:
        genai.configure(
            api_key=GeminiConfig.api_key
        )
        model = genai.GenerativeModel(model.name)
        response = model.generate_content(prompt + ' ' + chunk)
        return response.text


class Gpt4freeTranslator(AbstractTranslator):
    logger = logging.getLogger(LOGGER_PREFIX + __name__)

    @staticmethod
    def get_api_key(model: AIModel):
        if model.provider == 'GeminiPro':
            return GeminiConfig.api_key
        else:
            return None

    async def _process_chunk(
            self,
            model: AIModel,
            prompt: str,
            chunk: str
    ) -> str:
        response = requests.post(
            urljoin(
                G4FConfig.address, '/v1/chat/completions',
            ),
            json={
                'messages': [
                    {
                        'role': 'system',
                        'content': prompt
                    },
                    {
                        'role': 'user',
                        'content': chunk
                    }
                ],
                'model': model.name,
                'provider': model.provider,
                'stream': False,
                'temperature': 1,
                'max_tokens': 8192,
                'stop': [],
                'api_key': self.get_api_key(model),
                'web_search': True,
                'proxy': None
            }
        )
        if not response.ok:
            raise Exception(response.json())
        return response.json()['choices'][0]['message']['content']
