import httpx

from jinja2 import Template

from src.settings import UnisenderConfig


class UnisenderMailSender:
    @staticmethod
    async def _api_call(
            method_name: str,
            **kwargs
    ):
        data = {
            'api_key': UnisenderConfig.api_key,
            'format': 'json'
        }
        data.update(kwargs)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f'{UnisenderConfig.api_url}{method_name}',
                data=data
            )
            if response.is_error:
                raise Exception(response.text)
            if 'error' in response.json():
                raise Exception(response.json().get('error'))
            return response.json().get('result')

    @classmethod
    async def get_template_html(
            cls,
            template_id: str
    ) -> str:
        return (await cls._api_call(
            method_name='getTemplate',
            template_id=template_id
        )).get('body')

    @classmethod
    async def send(
            cls,
            to_address: str,
            from_address: str,
            from_name: str,
            subject: str,
            template_id: str,
            params: dict | None
    ):
        raw_template_html = await cls.get_template_html(template_id)
        template = Template(raw_template_html)
        body = template.render(params) if params else template.render()

        await cls._api_call(
            method_name='sendEmail',
            email=to_address,
            sender_name=from_name,
            sender_email=from_address,
            subject=subject,
            body=body,
            list_id=UnisenderConfig.list_id
        )
