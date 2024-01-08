from __future__ import annotations
from abc import ABC, abstractmethod
from actions import Action
from dataclasses import dataclass, asdict
import json


SCENARIO_PATH = "tree.json"


@dataclass
class Context:

    id_: str
    from_: Context | None
    to_: list[Context]
    question: str
    answer: str
    catch_text: list[str] # список фраз/слов на которые срабатывает переключение на данный контекст
    is_global: bool
    actions: list[Action]


class Manager:

    @staticmethod
    def parse_scenario() -> list[dict]:
        file = open(SCENARIO_PATH, encoding="utf-8")
        scenario = json.load(file)
        file.close()
        return scenario

    @staticmethod
    def _parse(self, options: list[dict], parent: str | None = None) -> list[Context]:
        new_questions = []
        for question in options:
            for question_name, question_data in question.items():
                q = Context(
                    id_=question_name,
                    from_=parent,
                    to_=self._parse(question_data["options"], question_name),
                    catch_text=question_data["catch_text"],
                    is_global=True,
                    question=question_data["question"],
                    answer=question_data["answer"],
                    actions=question_data["actions"]
                )
                new_questions.append(q)
                self.questions.append(q)
        return new_questions
