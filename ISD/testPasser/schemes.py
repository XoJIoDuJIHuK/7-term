from pydantic import BaseModel


class QuestionScheme(BaseModel):
    text: str
    correct_answers: list[str]
    incorrect_answers: list[str]
    variants: list[str]
    probable_correct_answers: list[str]
