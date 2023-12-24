from __future__ import annotations
from dataclasses import dataclass
import json
from uuid import uuid4


LOGS_PATH = "questions.log"
SCENARIO_PATH = "scenarios.json"
STARTING_QUESTION = "question_1"


@dataclass
class Message:

    text: str
    sent_by: str
    timestamp: str


@dataclass
class Question:

    key: str
    question: str
    answer: str
    options: list[Question]
    actions: list[str]


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

    def send(self, session: Session) -> str:
        for question in self.questions:
            if question.key == session.context:
                questions = [option.question for option in question.options]
                text = "\n".join(questions) + "\n"
                to_view = question.answer + text
                return to_view
        return "ЫЩРАЗУАР"


class Session:

    def __init__(self, user: User, bot: Bot):
        self.id = uuid4()
        self.history: list[Message] = []
        self.context = STARTING_QUESTION
        self.user = user
        self.bot = bot
        bot.sessions.append(self)

    def compose_message(self, text: str, sent_by: str) -> Message:
        message = Message(text=text, sent_by=sent_by, timestamp="sa")
        self.history.append(message)
        return message

    def loop(self) -> None:
        while True:
            bot_message = self.bot.send(self)
            message = self.compose_message(bot_message, sent_by="bot")
            self.user.get(message)
            user_message = self.user.send()
            self.compose_message(user_message, sent_by=f"USER {self.user.id}")
            for question in self.bot.questions:
                if user_message == question.question:
                    self.context = question.key


class User:

    def __init__(self):
        self.id = uuid4()
        self.session = None
        self.waiting = False

    def connect(self, bot: Bot) -> None:
        self.session = Session(self, bot)

    def disconnect(self) -> None:
        bot = self.session.bot
        bot.sessions.remove(self.session)
        self.session = None

    def send(self) -> str:
        if self.waiting:
            message = input(self.waiting).strip()
        else:
            message = ""
        self.waiting = False
        return message

    def get(self, message: Message) -> None:
        self.waiting = message.text

    def history(self) -> list[Message]:
        return self.session.history


bot = Bot()
u = User()
u.connect(bot)
bot.start()

