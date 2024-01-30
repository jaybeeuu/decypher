import pytest
from decypher.signature_word_map import SignatureWordMap, build_signature_word_map, get_word_signature

word_signature_tests = [
    ("three", "ABCDD"),
    ("apricot", "ABCDEFG"),
    ("these", "ABCDC"),
]

@pytest.mark.parametrize("word, expected", word_signature_tests)
def test_get_word_signature(word: str, expected: str):
    assert get_word_signature(word) == expected


signature_word_map_tests = [
    (["bee", "see", "#not", "feed"], {
        "ABB": ["BEE", "SEE"],
        "ABBC": ["FEED"]
    })
]

@pytest.mark.parametrize("words, expected", signature_word_map_tests)
def test_build_signature_word_map(words: str, expected: SignatureWordMap):
    assert build_signature_word_map(words) == expected
