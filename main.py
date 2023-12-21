from datetime import datetime, timezone
import json
from typing import Literal
from uuid import uuid4


Command = Literal["start", "ask", "message", "time", "amount", "leave", "run"]


class User:

    def __init__(self):
        self.id = uuid4()
        self.waiting = False
        self.question = None
        self.asked_questions = 0

    def message(self, message: str) -> None:
        self.question = message


class Bot:
    answers: str | list[str]
    last_command = None

    def __init__(self):
        self.waiting = False
        self.current_user = None
        self.user = None
        static = self.load_commands()
        self.available_commands = static["commands"]
        self.questions = static["questions"]

    def command(self, command: Command | None) -> None:
        if self.user:
            match command:
                case "run":
                    self.waiting = True
                    self.answers = list(self.available_commands.keys())
                case "start":
                    self.answers = "Привет! Меня зовут Веселбот, чем я могу быть полезен?"
                case "leave":
                    print("Всего доброго! Буду рад снова пообщаться ;)")
                    self.waiting = False
                case "time":
                    self.answers = f"Текущее время UTC: {self.get_current_utc_time()}"
                case "message":
                    self.answers = "Введите Ваше сообщение"
                    self.last_command = "message"
                case "amount":
                    self.answers = f"Кол-во заданных вопросов: {self.user.asked_questions}"
                case "ask":
                    self.answers = list(self.questions.keys())
                    self.last_command = "ask"
                case _:
                    try:
                        self.answers = self.questions[self.user.question]
                        if self.last_command == "ask":
                            self.user.asked_questions += 1
                        else:
                            self.answers = "Я не понимаю контекста. Введите команду текстом."
                    except KeyError:
                        if self.last_command == "message":
                            self.answers = "Ваше сообщение принято, мы сможем ответить на него позже. " \
                                           "Можете отправить ещё сообщение или ввести команду текстом"
                            self.log_message()
                        else:
                            self.answers = "Я не понимаю контекста. Введите команду текстом."
        else:
            raise Exception

    def compose_answer(self) -> dict[str, str] | str:
        if isinstance(self.answers, list):
            return {str(ind + 1): answer for ind, answer in enumerate(self.answers)}
        else:
            return self.answers

    def log_message(self) -> None:
        log_to_save = {
            "user_id": self.user.id,
            "message": self.user.question,
            "time": self.get_current_utc_time()
        }
        logfile = open("questions.log", "a")
        logfile.write(str(log_to_save) + "\n")
        logfile.close()

    def parse_command(self, question: str) -> Command | None:
        try:
            return self.available_commands[question]
        except KeyError:
            return None

    @staticmethod
    def get_current_utc_time() -> str:
        return datetime.now(timezone.utc).strftime("%H:%M:%S")

    @staticmethod
    def load_commands() -> dict[str, dict[str, str | Command]]:
        file = open("tree.json", encoding="utf-8")
        data = json.load(file)
        file.close()
        return data


class Session:

    def __init__(self):
        self.id = uuid4()
        self.bot = Bot()
        self.bot_prefix = "\t\t\t\t\t\t"

    def view(self, answers_dict: dict[str, str]) -> str:
        options = ""
        for ind, answer in answers_dict.items():
            options += f"\t{self.bot_prefix}({ind}) {answer}"
            options += "\n"
        return f"{self.bot_prefix}Доступны для выбора следуюшие опции:\n" + options

    def loop(self) -> None:
        while self.bot.waiting:
            answers = self.bot.compose_answer()
            if isinstance(answers, dict):
                to_view = self.view(answers)
                raw_message = input(to_view).strip()
                if raw_message in answers.keys():
                    message = answers[raw_message]
                elif raw_message in answers.values():
                    message = raw_message
                else:
                    message = "Я не понял Ваш вопрос"
            else:
                message = input(self.bot_prefix + answers + "\n").strip()
                message = message
            self.bot.user.message(message)
            command = self.bot.parse_command(self.bot.user.question)
            self.bot.command(command)
            self.bot.user.waiting = False

    def start(self):
        self.bot.command("run")
        if self.bot.user:
            self.loop()
        else:
            raise Exception

    def connect_user(self, user: User | None) -> None:
        if isinstance(user, User):
            self.bot.user = user
        else:
            raise Exception


if __name__ == "__main__":

    session = Session()
    user = User()
    session.connect_user(user)
    session.start()
