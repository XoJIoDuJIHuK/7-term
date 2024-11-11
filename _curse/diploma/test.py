import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import Article, AIModel, StylePrompt, Language
from src.util.storage.classes import RedisHandler
from src.util.translator.classes import Gpt4freeTranslator

prompt = (
    'Translate following text from english to belarusian: Rommel was a highly'
    ' decorated officer in World War I and was awarded the Pour le Mérite for'
    ' his actions on the Italian Front. In 1937, he published his classic'
    ' book on military tactics, Infantry Attacks, drawing on his experiences'
    ' in that war. In World War II, he commanded the 7th Panzer Division'
    ' during the 1940 invasion of France. His leadership of German and Italian'
    ' forces in the North African campaign established his reputation as one'
    ' of the ablest tank commanders of the war, and earned him the nickname'
    ' der Wüstenfuchs, "the Desert Fox". Among his British adversaries he had'
    ' a reputation for chivalry, and his phrase "war without hate" has been'
    ' uncritically used to describe the North African campaign.[2] A number'
    ' of[weasel words] historians have since rejected the phrase as a myth'
    ' and uncovered numerous examples of German war crimes and abuses towards'
    ' enemy soldiers and native populations in Africa during the conflict.[3]'
    ' Other historians note that there is no clear evidence Rommel was'
    ' involved or aware of these crimes,[4] with some pointing out that the'
    ' war in the desert, as fought by Rommel and his opponents, still came'
    ' as close to a clean fight as there was in World War II.[5] He later'
    ' commanded the German forces opposing the Allied cross-channel invasion'
    ' of Normandy in June 1944.'
)

# import google.generativeai as genai
#
# genai.configure(api_key='AIzaSyBmKikk9iZfTFCzUL7wPLFY1lcJNNah4VM')
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content(prompt)
#
# print(response.text)

async def main():
    async with get_session() as db:
        article = (await db.execute(select(Article).filter_by(id=uuid.UUID('c10394b8-5cdd-4d88-9d25-0e654678ab64')))).scalars().first()
        model = (await db.execute(select(AIModel).filter_by(id=1))).scalars().first()
        prompt = (await db.execute(select(StylePrompt).filter_by(id=1))).scalars().first()
        language = (await db.execute(select(Language).filter_by(id=5))).scalars().first()

        await Gpt4freeTranslator().translate(
            text='hello, it\'s me, Mario',
            source_language=None,
            target_language=language,
            model=model,
            prompt_object=prompt
        )

if __name__ == '__main__':
    asyncio.run(main())
