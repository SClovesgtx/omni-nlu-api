from api import patterns_matcher
import pytest

patterns = [
    (
        "ContactInfo:email",
        [
            "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b",
            "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
        ],
    )
]
sentence = "olá meu email é clovesgtx@gmail.com"
result = [{"ContactInfo:email": ["clovesgtx@gmail.com"]}]


@pytest.mark.parametrize("patterns, sentence, result", [(patterns, sentence, result)])
def test_patterns_matcher(patterns, sentence, result):
    assert patterns_matcher(patterns, sentence) == result
