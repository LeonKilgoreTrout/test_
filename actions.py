from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


ASSERTION_MESSAGE = "Переданный объект имеет не подходящий тип"
LOGS_PATH = "questions.log"


class Action(ABC):
    """ Выполняет дополнительную логику бота.
     При необходимости можно подтянуть зависимости с которыми необходимо работать """

    @abstractmethod
    def run(self) -> Any:
        pass

    @abstractmethod
    def set_dependency(self, dependency: Any) -> None:
        pass


class SaveLogAction(Action):

    def __init__(self):
        self.dependency = None

    def run(self) -> None:
        assert isinstance(self.dependency, str), ASSERTION_MESSAGE
        logfile = open(LOGS_PATH, "a", encoding="utf-8")
        logfile.write(str(self.dependency) + "\n")
        logfile.close()

    def set_dependency(self, dependency: Any):
        self.dependency = dependency


class GetCurrentTimeAction(Action):

    def run(self) -> str:
        current_date = datetime.now(timezone.utc).strftime("%H:%M:%S")
        return current_date

    @abstractmethod
    def set_dependency(self, dependency: Any) -> None:
        pass


# class Ge