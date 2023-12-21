import pytest
# from datetime import datetime
from main import Session, User


# def read_len():
#     with open("questions.log", "r") as log_file:
#         return sum(1 for _ in log_file)


@pytest.fixture()
def test_session():
    conversation = Session()
    user = User()
    conversation.connect_user(user)
    yield conversation
    del conversation


def test_start_conversation(test_session):
    test_session.bot.command("start")
    assert test_session.bot.answers == "Привет! Меня зовут Веселбот, чем я могу быть полезен?"
    assert test_session.bot.user.question is None


def test_ask_question(test_session):
    options = [
        "В какой компании ты работаешь?",
        "Чем компания занимается?",
        "Кто тебя создал?",
    ]
    test_session.bot.command("ask")
    assert test_session.bot.answers == options
