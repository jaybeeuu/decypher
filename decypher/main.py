
from typing import Iterable

from decypher.word_index import WordIndex


def load_words(file: str) -> Iterable[str]:
  with open(file, mode="r") as words:
    return (word for word in words)

def get_word_index(file: str) -> WordIndex:
  try
    with (open(file, mode="r")):
