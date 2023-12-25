from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from uuid import uuid4


LOGS_PATH = "questions.log"
SCENARIO_PATH = "scenarios.json"
STARTING_QUESTION = "question_1"


@dataclass
class Message:

    text: str
    sent_by: str
    time: str


@dataclass
class Question:

    key: str
    question: str
    answer: str
    options: list[Question]
    actions: list[str]


def log_message(message: Message) -> None:
    log_to_save = asdict(message)
    logfile = open(LOGS_PATH, "a", encoding="utf-8")
    logfile.write(str(log_to_save) + "\n")
    logfile.close()


def get_current_utc_time() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


class Bot:

    questions: list[Question]
    tree: list[Question]

    def __init__(self):
        self.running = False
        self.sessions: list[Session] = []
        self.id = 1

    def start(self) -> None:
        self.running = True
        self.questions = []
        self.tree = self._parse_questions()
        self._loop()

    def stop(self) -> None:
        self.running = False

    def _loop(self) -> None:
        while self.running:
            for session in self.sessions:
                session.loop()

    @staticmethod
    def parse_scenario() -> list[dict]:
        file = open(SCENARIO_PATH, encoding="utf-8")
        scenario = json.load(file)
        file.close()
        return scenario

    def _parse(self, options: list[dict]) -> list[Question]:
        new_questions = []
        for question in options:
            for question_name, question_data in question.items():
                q = Question(
                    key=question_name,
                    question=question_data["question"],
                    answer=question_data["answer"],
                    options=self._parse(question_data["options"]),
                    actions=question_data["actions"]
                )
                new_questions.append(q)
                self.questions.append(q)
        return new_questions

    def _parse_questions(self) -> list[Question]:
        scenario = self.parse_scenario()
        questions = self._parse(scenario)
        return questions

    def send(self, session: Session) -> Message:
        for question in self.questions:

            if question.key == session.context:

                questions = [option.question for option in question.options if option.question != "_"]
                text = "\n".join(questions) + "\n"
                message = question.answer + text
                if question.actions:
                    for action in question.actions:
                        message += session.action(action)
                return Message(message, str(self.id), get_current_utc_time())
            else:
                pass


class Session:

    def __init__(self, user: User, bot: Bot):
        self.id = uuid4()
        self.history: list[Message] = []
        self.context = STARTING_QUESTION
        self.user = user
        self.bot = bot
        self.running = True
        bot.sessions.append(self)

    def loop(self) -> None:
        while self.running:
            bot_message = self.bot.send(self)
            self.history.append(bot_message)
            self.user.get(bot_message)
            user_message = self.user.send()
            self.history.append(user_message)
            context_not_changed = True
            for question in self.bot.questions:
                if user_message.text == question.question:
                    self.context = question.key
                    context_not_changed = False
            if context_not_changed:
                if bot_message.text == "Введите Ваше сообщение\n":
                    self.context = "question_free"
                else:
                    if self.running:
                        print("К сожалению у меня не получилось найти то, что Вам нужно.")
                        self.context = STARTING_QUESTION
        self.bot.running = False

    def action(self, action: str) -> str:
        available_to_ask = [
            "В какой компании ты работаешь?",
            "Чем компания занимается?",
            "Кто тебя создал?"
        ]
        match action:
            case "save_log":
                log_message(self.history[-1])
                return ""
            case "time":
                return get_current_utc_time()
            case "amount":
                amount = 0
                for message in self.history:
                    if message.sent_by == str(self.user.id):
                        if message.text in available_to_ask:
                            amount += 1
                return str(amount)
            case "leave":
                self.running = False
                self.user.disconnect()
                return ""


class User:

    def __init__(self):
        self.id = uuid4()
        self.session = None
        self.waiting = False

    def connect(self, bot: Bot) -> None:
        self.session = Session(self, bot)

    def disconnect(self) -> None:
        del self.session
        self.session = None

    def send(self) -> Message:
        if self.waiting:
            message = input(self.waiting).strip()
        else:
            message = ""
        self.waiting = False
        return Message(message, str(self.id), get_current_utc_time())

    def get(self, message: Message) -> None:
        self.waiting = message.text

    def history(self) -> list[Message]:
        return self.session.history


if __name__ == "__main__":
    bot = Bot()
    u = User()
    u.connect(bot)
    bot.start()

