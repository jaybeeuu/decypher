import functools
from typing import Iterable

def get_word_signature(word: str) -> str:
  unique_letter_index = 65
  letters = {}
  signature = ""

  for char in word:
    if char not in letters:
      letters[char] = chr(unique_letter_index)
      unique_letter_index += 1

    signature += f'{letters[char]}'

  return signature

type WordIndex = dict[str, list[str]]

def word_index_reducer(index: WordIndex, word_signature: tuple[str, str]) -> WordIndex:
  word, signature = word_signature

  if signature not in index:
    index[signature] = []

  index[signature].append(word)

  return index

def build_word_index(words: Iterable[str]) -> WordIndex:
  signatures = ((word, get_word_signature(word)) for word in words)

  return functools.reduce(word_index_reducer, signatures, {})