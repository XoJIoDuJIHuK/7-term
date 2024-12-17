import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/known-questions', response_class=HTMLResponse)
async def get_known_questions(request: Request):
    with open('answers.json', 'r') as file:
        file_content = file.read() or '{}'
        questions = json.loads(file_content)
    return templates.TemplateResponse(
        'index.html',
        {'request': request, 'questions': questions}
    )