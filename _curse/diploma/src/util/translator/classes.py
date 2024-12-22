import json
from urllib.parse import urljoin

# import google.generativeai as genai
import httpx

from src.database.models import (
    AIModel,
)
from src.logger import get_logger
from src.settings import (
    LOGGER_PREFIX,
    GeminiConfig,
    G4FConfig,
)
from src.util.translator.abstract import AbstractTranslator


# class GeminiTranslator(AbstractTranslator):
#     logger = get_logger(LOGGER_PREFIX + __name__)
#
#     async def _process_chunk(
#             self,
#             model: AIModel,
#             prompt: str,
#             chunk: str
#     ) -> str:
#         genai.configure(
#             api_key=GeminiConfig.api_key
#         )
#         model = genai.GenerativeModel(model.name)
#         response = model.generate_content(prompt + ' ' + chunk)
#         return response.text


class Gpt4freeTranslator(AbstractTranslator):
    logger = get_logger(LOGGER_PREFIX + __name__)

    @staticmethod
    def get_api_key(model: AIModel):
        if model.provider == 'GeminiPro':
            return GeminiConfig.api_key
        else:
            return None

    async def get_response(self, request_payload: dict):
        async with httpx.AsyncClient(timeout=120.0) as client:
            return await client.post(
                urljoin(G4FConfig.address, '/v1/chat/completions'),
                json=request_payload,
            )

    async def _process_chunk(
            self,
            model: AIModel,
            prompt: str,
            chunk: str
    ) -> str:
        request_payload = {
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
        self.logger.info(f'Translating chunk: {chunk}')
        response = await self.get_response(request_payload)
        self.logger.info(f'Got response: {response}')
        if not response.is_success:
            raise Exception(json.dumps(response.json()))
        answer = response.json()['choices'][0]['message']['content']
        self.logger.info(f'Returned answer: {answer}')
        return answer
