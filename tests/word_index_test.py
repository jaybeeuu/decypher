import pytest
from decypher.word_index import WordIndex, build_word_index, get_word_signature

word_signature_tests = [
    ("three", "ABCDD"),
    ("apricot", "ABCDEFG"),
    ("these", "ABCDC"),
]

@pytest.mark.parametrize("word, expected", word_signature_tests)
def test_get_word_signature(word: str, expected: str):
    assert get_word_signature(word) == expected


word_index_tests = [
    (["bee", "see", "feed"], {
        "ABB": ["bee", "see"],
        "ABBC": ["feed"]
    })
]

@pytest.mark.parametrize("words, expected", word_index_tests)
def test_build_word_index(words: str, expected: WordIndex):
    assert build_word_index(words) == expected