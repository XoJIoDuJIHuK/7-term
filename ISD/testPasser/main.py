import json
import logging
import os

from bs4 import BeautifulSoup, Tag

import requests

from schemes import QuestionScheme


logger = logging.getLogger(__name__)
answers: dict[str, dict] = {}


def ask_gpt(question: QuestionScheme, multiple_choice: bool = True):
    prompt = (
        f'Дай ответ на следующий вопрос: {question.text}. Варианты ответа: '
        f'{question.variants}. Известные правильные варианты: '
        f'{question.correct_answers}. Известные неправильные '
        f'варианты: {question.incorrect_answers}. В ответе напиши '
        f'массив из строк-правильных вариантов. Не рассуждай, не пиши '
        f'"Конечно! Вот правильный ответ" и так далее и не изменяй текст '
        f'вариантов ответа. Только массив из наиболее вероятно правильных '
        f'ответов. '
    )
    if not multiple_choice:
        prompt += 'Уточнение: правильный вариант ответа может быть только один'
    request = {
        'messages': [
            {
                'role': 'system',
                'content': ''
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'model': os.environ.get('MODEL_NAME'),
        'provider': 'DDG',
        'stream': False,
        'temperature': 1,
        'max_tokens': 8192,
        'stop': [],
        'api_key': None,
        'web_search': True,
        'proxy': None
    }
    response = requests.post(
        'http://localhost:1337/v1/chat/completions',
        json=request
    )
    if not response.ok:
        logger.error(response.json())
        return
    answers_json = response.json()['choices'][0]['message']['content']
    answers_list = json.loads(answers_json.replace('\'', '"'))
    for answer in answers_list:
        if answer not in question.variants:
            logger.error(
                f'Гопота опять галлюцинирует. Варианты '
                f'{question.variants}, она выдала {answer}'
            )
        else:
            question.probable_correct_answers.append(answer)



def process_answer(answer_element: Tag):
    def remove_duplicates(answer_object: QuestionScheme, attribute: str):
        arr = list(set(getattr(answer_object, attribute)))
        setattr(answer_object, attribute, arr)

    question = answer_element.select_one('div.qtext > p').text.strip()
    variants = answer_element.select('fieldset > div.answer > div')
    if question in answers:
        existing_answer = QuestionScheme.model_validate(answers[question])
        if existing_answer.correct_answers:
            return
    else:
        existing_answer = QuestionScheme(
            text=question,
            correct_answers=[],
            incorrect_answers=[],
            variants=[],
            probable_correct_answers=[],
        )
    for variant in variants:
        variant_text = variant.text.strip()
        if variant_text not in existing_answer.variants:
            existing_answer.variants.append(variant_text)
        if (
            'incorrect' in variant.attrs.get('class') and
            variant.text not in existing_answer.incorrect_answers
        ):
            existing_answer.incorrect_answers.append(variant_text)
        elif 'correct' in variant.attrs.get('class'):
            existing_answer.correct_answers.append(variant_text)

    if not existing_answer.correct_answers:
        logger.error(
            f'О великий чатгопник, помоги ответить на вопрос {question}'
        )
        ask_gpt(existing_answer, multiple_choice=False)
        logger.error(
            f'Гопник ответил: {existing_answer.probable_correct_answers}'
        )

    for key in ['correct_answers', 'incorrect_answers']:
        remove_duplicates(existing_answer, key)
    answers[question] = existing_answer.model_dump()



if __name__ == '__main__':
    with open('answers.json', 'r') as file:
        file_content = file.read()
        if file_content:
            answers = json.loads(file_content)
    pass
    url = 'https://dist.belstu.by/mod/quiz/review.php?attempt=1116357&cmid=31663'
    cookies = {
        '_ga': 'GA1.2.1494649560.1727930800',
        # '_gid': 'GA1.2.953540696.1732721964',
        'MoodleSession': 'v7k7petin1b236l9l4h6v650on',  # maybe this one changes
        'MOODLEID1_': '%25C2%25CA%25B0t%2503%25C7%2508%25CC'
    }
    html_text = requests.get(
        url=url,
        cookies=cookies,
    ).text
    # with open('index.html', 'r') as file:
    #     html_text = file.read()
    soup = BeautifulSoup(html_text, 'html.parser')
    list_items = soup.select('.que.multichoice.deferredfeedback')
    for wrapper in list_items:
        process_answer(wrapper)
    with open('answers.json', 'w') as file:
        file.write(json.dumps(answers, ensure_ascii=False))