from dataclasses import dataclass
import json
import re
from typing import Callable, Generator
from decypher.signature_word_map import SignatureWordMap, build_signature_word_map, get_word_signature


def load_signature_word_map_from_words_file(file: str) -> SignatureWordMap:
  with open(file, mode="r") as words:
    return build_signature_word_map(words)


def get_signature_word_map(
  words_file_name: str,
  signature_word_map_file_name: str
) -> SignatureWordMap:
  try:
    with open(signature_word_map_file_name, mode="r") as signature_word_map_file:
      return json.load(signature_word_map_file)

  except FileNotFoundError:
    index = load_signature_word_map_from_words_file(words_file_name)

    with open(signature_word_map_file_name, "w") as signature_word_map_file:
      json.dump(index, signature_word_map_file)

    return index


type CypherTable = dict[str, str]


@dataclass
class DecypherState():
  cypher_words: list[str]
  signature_word_map: SignatureWordMap
  current_word_index: int
  cypher_table: CypherTable

  def to_tuple(self) -> tuple[list[str], SignatureWordMap, int, CypherTable]:
    return (
      self.cypher_words,
      self.signature_word_map,
      self.current_word_index,
      self.cypher_table
    )

  def __str__(self):
    return f"DecypherSate(current_word={self.cypher_words[self.current_word_index]}, cypher_table={self.cypher_table})"


def get_cypher_table_for_pair(cypher: str, plain: str) -> CypherTable:
  return dict(zip(cypher, plain))


def tables_conflict(left: CypherTable, right: CypherTable) -> bool:
  mismatching_keys = next(
    (key for key in left.keys() if key in right and left[key] != right[key]),
    None
  ) != None

  left_values = { *left.values() }
  repeats_values = next(
    (key for key in right.keys() if key not in left and right[key] in left_values),
    None
  ) != None
  return mismatching_keys | repeats_values

def all_letters_in_table(cypher_word: str, cypher_table: CypherTable) -> bool:
  return all(letter in cypher_table for letter in cypher_word)

def decypher_next_word(
  state: DecypherState,
  on_cypher_table: Callable[[CypherTable], None] = lambda table: None
) -> CypherTable | None:
  cypher_words, signature_word_map, current_word_index, cypher_table = state.to_tuple()

  if current_word_index == len(cypher_words):
    return cypher_table

  cypher_word = cypher_words[current_word_index]
  current_word_signature = get_word_signature(cypher_word)
  candidate_words = signature_word_map[current_word_signature]

  if len(candidate_words) == 0:
    raise RuntimeError(f"Unrecognised word signature: {get_word_signature(cypher_word)} ({cypher_word})")

  if all_letters_in_table(cypher_word, cypher_table):
    if decypher_text_with_table(cypher_word, cypher_table) in candidate_words:
      return decypher_next_word(DecypherState(
        cypher_words=cypher_words,
        signature_word_map=signature_word_map,
        current_word_index=current_word_index + 1,
        cypher_table=cypher_table,
      ), on_cypher_table)
    else:
      return None

  for plain_word in candidate_words:
    candidate_table = get_cypher_table_for_pair(cypher_word, plain_word)
    candidate_conflicts_with_current = tables_conflict(candidate_table, cypher_table)

    if candidate_conflicts_with_current:
      continue

    next_table = { **cypher_table, **candidate_table }

    on_cypher_table(next_table)

    # print(f"current_word_index={current_word_index}, cypher_word={cypher_word}, plain_word={plain_word}, candidate_table={candidate_table}, conflicts={candidate_conflicts_with_current}, next_table={next_table}")

    final_cypher_table = decypher_next_word(DecypherState(
      cypher_words=cypher_words,
      signature_word_map=signature_word_map,
      current_word_index=current_word_index + 1,
      cypher_table=next_table,
    ), on_cypher_table)

    if final_cypher_table != None:
      return final_cypher_table

  return None


def get_nonoverlapping_words(words: list[str]) -> Generator[str, None, None]:
  letters_so_far: set[str] = set()

  for word in words:
    new_letters = letters_so_far | { *word }

    if new_letters != letters_so_far:
      yield word
      letters_so_far = new_letters


def get_cypher_table(
  cypher_text: str,
  signature_word_map: SignatureWordMap,
  on_cypher_table: Callable[[CypherTable], None] = lambda table: None
) -> CypherTable | None:
  unsorted = set(
    [re.sub("[^A-Z]", "", word) for line in cypher_text.splitlines() for word in line.split(" ")]
  )

  # print(f"\n{unsorted}\n")

  cypher_words = sorted(
    [word for word in unsorted if word],
    key=lambda word: len(signature_word_map[get_word_signature(word)])
  )
  # nonoverlapping_cypher_words = [*get_nonoverlapping_words(cypher_words)]

  # print([(
  #   word,
  #   len(signature_word_map[get_word_signature(word)])
  # ) for word in cypher_words])

  return decypher_next_word(DecypherState(
      cypher_words=cypher_words,
      signature_word_map=signature_word_map,
      current_word_index=0,
      cypher_table={ }
    ), on_cypher_table)


def decypher_text_with_table(cypher_text: str, cypher_table: CypherTable) -> str:
  return "".join(
    (cypher_table[char] if char in cypher_table else char for char in cypher_text)
  )


class UnableToDecypherError(RuntimeError):
  pass


def decypher(
  cypher_text: str,
  words_file_name: str="./words.txt",
  word_index_file_name: str="./signature_word_map.txt",
  on_cypher_table: Callable[[CypherTable], None] = lambda table: None
) -> str:
  word_index = get_signature_word_map(
    words_file_name,
    word_index_file_name
  )
  cypher_table = get_cypher_table(
    cypher_text,
    word_index,
    on_cypher_table
  )

  if cypher_table == None:
    raise UnableToDecypherError("Unable to decypher the text.")

  return decypher_text_with_table(cypher_text, cypher_table)
