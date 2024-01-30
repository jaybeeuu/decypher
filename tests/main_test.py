import pytest
import json
import os
import pathlib
from typing import Iterable, TypedDict, Unpack
from decypher.main import CypherTable, get_signature_word_map, tables_conflict
from decypher.signature_word_map import SignatureWordMap

word_index_tests = [
  (["bee", "see", "feed"], {
    "ABB": ["BEE", "SEE"],
    "ABBC": ["FEED"]
  })
]

def with_linesep(lines: Iterable[str]) -> Iterable[str]:
  return (f'{line}{os.linesep}' for line in lines)

class RunGetWordIndexKwargs(TypedDict):
  words: list[str] | None
  cached_index: SignatureWordMap | None

class RunGetWordIndexResult(TypedDict):
  index: SignatureWordMap
  words_file_path: pathlib.Path
  index_file_path: pathlib.Path


def run_get_word_index(
  tmp_path: pathlib.Path,
  **kwargs: Unpack[RunGetWordIndexKwargs]
) -> RunGetWordIndexResult:
  cached_index = kwargs["cached_index"]
  words = kwargs["words"]

  words_file_path = tmp_path / "words.txt"
  index_file_path = tmp_path / "index.json"

  if words is not None:
    with open(words_file_path, "w") as words_file:
      words_file.writelines(with_linesep(words))

  if cached_index is not None:
    with open(index_file_path, "w") as index_file:
      json.dump(cached_index, index_file)

  index = get_signature_word_map(words_file_path.as_posix(), index_file_path.as_posix())

  return {
    "index": index,
    "words_file_path": words_file_path,
    "index_file_path": index_file_path
  }


def test_get_word_index__should_return_an_index_generated_from_the_words(tmp_path: pathlib.Path):
  result = run_get_word_index(tmp_path, words=["bee", "see", "feed"], cached_index=None)

  assert result["index"] == {
    "ABB": ["BEE", "SEE"],
    "ABBC": ["FEED"]
  }


def test_get_word_indextest_get_word_index__should_write_the_index_to_disk(tmp_path: pathlib.Path):
  result = run_get_word_index(tmp_path, words=["bee", "see", "feed"], cached_index=None)

  assert result["index_file_path"].exists()

  with open(result["index_file_path"], "r") as index_file:
    assert json.load(index_file) == {
      "ABB": ["BEE", "SEE"],
      "ABBC": ["FEED"]
    }


def test_get_word_index__should_return_the_cached_index_if_one_exists(tmp_path: pathlib.Path):
  cached_index = {
    "ABB": ["BEE", "SEE"],
    "ABBC": ["FEED"]
  }
  result = run_get_word_index(tmp_path, words=[], cached_index=cached_index)

  assert result["index"] == cached_index

tables_conflict_samples: list[tuple[CypherTable, CypherTable, bool]] = [
  ({}, {}, False),
  ({ "A": "B" }, { "A": "B" }, False),
  ({ "A": "B" }, { }, False),
  ({ "A": "B" }, { "C": "D" }, False),
  ({ "A": "D" }, { "C": "D" }, True),
  ({ "A": "B" }, { "A": "C" }, True)
]

@pytest.mark.parametrize("left, right, expected", tables_conflict_samples)
def test_tables_conflict(
  left: CypherTable,
  right: CypherTable,
  expected: bool
):
  assert tables_conflict(left, right) == expected
