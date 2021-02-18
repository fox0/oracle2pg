# import logging
import string

# log = logging.getLogger(__name__)
STRING_LETTERS = string.ascii_letters + string.octdigits + '_'


def tokenizer(text: str):
    text = text.lower()
    i = 0
    try:
        while True:
            while text[i].isspace():
                i += 1
            if text[i] in '(),;':
                yield text[i]
                i += 1
                continue
            if text[i] not in STRING_LETTERS:
                raise ValueError(text[i])
            b = i
            i += 1
            while text[i] in STRING_LETTERS:
                i += 1
            yield text[b:i]
    except IndexError:
        pass
