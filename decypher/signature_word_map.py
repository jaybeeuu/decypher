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

type SignatureWordMap = dict[str, list[str]]

def word_index_reducer(
  index: SignatureWordMap,
  word_signature: tuple[str, str]
) -> SignatureWordMap:
  word, signature = word_signature

  if signature not in index:
    index[signature] = []

  index[signature].append(word.upper())

  return index

def build_signature_word_map(words: Iterable[str]) -> SignatureWordMap:
  stripped_words = (word.strip() for word in words if not word.startswith("#"))
  signatures = ((word, get_word_signature(word)) for word in stripped_words)

  return functools.reduce(word_index_reducer, signatures, {})