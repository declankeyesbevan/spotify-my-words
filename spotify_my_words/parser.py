import re

from collections import Counter


MAX_LENGTH = 30


def parse_message(message):
    cleaned = re.sub(r'([\W\d])+', '', message)
    if len(cleaned) > MAX_LENGTH:
        cleaned = cleaned[:MAX_LENGTH]
    cleaned = [letter.lower() for letter in cleaned]

    count = Counter()
    count.update(cleaned)
    return _get_indices_and_limit(cleaned, count), len(cleaned)


def _get_indices_and_limit(cleaned, count):
    token_indices = {}
    for token, limit in count.items():
        indices = [index for index, value in enumerate(cleaned) if value == token]
        token_indices.update({token: {'indices': indices, 'limit': limit}})
    return token_indices
