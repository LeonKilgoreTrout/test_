from __future__ import annotations
from abc import ABC, abstractmethod
from actions import Action
from dataclasses import dataclass, asdict
from exceptions import ContextNotFoundException
import json
from matching import SimpleMatchingRule
from typing import Any


SCENARIO_PATH = "scenarios.json"


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

    current_context: Context = None

    def __init__(self):
        scenario = self._parse_scenario()
        self.contexts = []
        self._parse(scenario, parent=None)

    @staticmethod
    def _parse_scenario() -> list[dict]:
        file = open(SCENARIO_PATH, encoding="utf-8")
        scenario = json.load(file)
        file.close()
        return scenario

    def _parse(self, options: list[dict], parent: str | None = None) -> list[Context]:
        new_questions = []
        for question in options:
            for question_name, question_data in question.items():
                question = question_data["question"]
                q = Context(
                    id_=question_name,
                    from_=parent,
                    to_=self._parse(question_data["options"], question_name),
                    catch_text=question_data.get("catch_text", question),
                    is_global=question_data.get("global", True),
                    question=question,
                    answer=question_data["answer"],
                    actions=question_data["actions"]
                )
                new_questions.append(q)
                self.contexts.append(q)
        return new_questions

    def start(self):
        self.activate_context("question_1")
        context = self.current_context
        while True:
            bot_speech = context.answer
            user_speech = input(bot_speech)
            for text in context.catch_text:
                mr = SimpleMatchingRule(text)
                if mr.run(user_speech):
                    self.current_context = context
            self._run()

    def activate_context(self, context_to_activate: str):
        for context in self.contexts:
            if context.id_ == context_to_activate:
                self.current_context = context
        if self.current_context is None:
            raise ContextNotFoundException

    def _run(self):
        for action in self.current_context.actions:
            action.run()


manager = Manager()
manager.start()