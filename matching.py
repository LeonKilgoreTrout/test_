from abc import ABC, abstractmethod
from fuzzywuzzy import fuzz


class MatchingRule(ABC):
    """ Правило проверки текста """

    @abstractmethod
    def run(self, text: str) -> bool:
        pass

    @abstractmethod
    def set_threshold(self, threshold: int) -> None:
        pass


class SimpleMatchingRule(MatchingRule):

    def __init__(self, text: str):
        self.text = text

    def run(self, text: str) -> bool:
        return text == self.text

    def set_threshold(self, threshold: int) -> None:
        pass


class LevenshteinMatchingRule(MatchingRule):

    def __init__(self, text: str):
        self.text = text
        self.threshold = 100

    def run(self, text: str) -> bool:
        checking_result = fuzz.WRatio(text, self.text)
        result = True if checking_result >= self.threshold else False
        return result

    def set_threshold(self, threshold: int) -> None:
        self.threshold = threshold


class MLMatchingRule(MatchingRule):

    def __init__(self, text: str):
        self.text = text
        self.threshold = 100

    def run(self, text: str) -> bool:
        ...

    def set_threshold(self, threshold: int) -> None:
        self.threshold = threshold
