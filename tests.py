import pytest
from datetime import datetime
# from ... import Session


class Session:
    pass


def read_len():
    with open("questions.log", "r") as log_file:
        return sum(1 for _ in log_file)


@pytest.fixture()
def test_session():
    conversation = Session()
    yield conversation
    del conversation


def test_start_conversation(test_session):
    assert test_session.bot.command("start") == "Привет! Меня зовут Веселбот, чем я могу быть полезен?"


def test_ask_question(test_session):
    options = ("(1) В какой компании ты работаешь?", "(2) Чем компания занимается?", "(3) Кто тебя создал?")
    assert test_session.bot.command("ask") == "\n".join(options)


def test_ask_question_work_in_company(test_session):
    gold_answer = "Неовокс Технологии"

    test_session.bot.command("ask")
    test_session.user.message(1)
    assert test_session.bot.answer == gold_answer

    test_session.bot.command("ask")
    test_session.user.message("В какой компании ты работаешь?")
    assert test_session.bot.answer == gold_answer


def test_ask_question_company_sphere(test_session):
    gold_answer = "Разработкой голосовых ботов"

    test_session.bot.command("ask")
    test_session.user.message(2)
    assert test_session.bot.answer == gold_answer

    test_session.bot.command("ask")
    test_session.user.message("Чем компания занимается?")
    assert test_session.bot.answer == gold_answer


def test_ask_question_creator(test_session):
    gold_answer = "Разработчик"

    test_session.bot.command("ask")
    test_session.user.message(3)
    assert test_session.bot.answer == gold_answer

    test_session.bot.command("ask")
    test_session.user.message("Кто тебя создал?")
    assert test_session.bot.answer == gold_answer


def test_ask_question_not_in_pool(test_session):
    gold_answer = "Не могу найти подходящий вопрос"

    test_session.bot.command("ask")
    test_session.user.message(4)
    assert test_session.bot.answer == gold_answer

    test_session.bot.command("ask")
    test_session.user.message("Что ты сегодня ел?")
    assert test_session.bot.answer == gold_answer


def test_message(test_session):
    test_session.bot.command("message")
    assert test_session.bot.answer == "Введите Ваше сообщение"
    length_1 = read_len()
    test_session.user.message("Любое сообщение")
    assert test_session.bot.answer == "Ваше сообщение принято, \
     мы сможем ответить на него позже"
    length_2 = read_len()
    assert length_2 > length_1


def test_current_time(test_session):
    test_session.bot.command("time")
    try:
        datetime.strptime(test_session.bot.answer, "%H:%M:%S")
    except ValueError:
        assert False


def test_total_questions(test_session):
    amount_text = "Текущее кол-во заданных вопросов: "

    test_session.bot.command("amount")
    assert test_session.bot.answer == amount_text + "0"

    test_session.bot.command("ask")
    test_session.user.message(2)
    test_session.bot.command("amount")
    assert test_session.bot.answer == amount_text + "1"

    test_session.bot.command("ask")
    test_session.user.message(2)
    test_session.bot.command("ask")
    test_session.user.message(4)

    test_session.bot.command("amount")
    assert test_session.bot.answer == amount_text + "3"


def test_leave_conversation(test_session):

    test_session.bot.command("leave")
    assert test_session.bot.answer == "Всего доброго! Буду рад снова пообщаться ;)"
