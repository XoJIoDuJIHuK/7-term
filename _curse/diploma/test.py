from src.util.storage.classes import RedisHandler

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

# import asyncio
# async def foo():
#     pubsub = RedisHandler().get_pubsub()
#     await pubsub.subscribe('notifications')
#     while True:
#         message = await pubsub.get_message(timeout=1.0)
#         if message:
#             print(message)
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(foo())