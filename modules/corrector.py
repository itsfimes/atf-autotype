import re

def correct_text(text: str) -> str:
    text = replace_common_incorrect_characters(text)
    text = correct_spaces(text)
    text = fix_lowercase_letters(text)
    return text


def replace_common_incorrect_characters(text: str) -> str:
    return text.replace("\n", " ").replace("|", "").replace("0", "o").replace("£", "f").replace(" ,", ",")


def fix_lowercase_letters(text: str) -> str:
    if not len([c for c in text if c.isupper()]) > 2:
        return text.lower()
    return text

def correct_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text)



def correct_sro(text: str) -> str:
    result = []
    i = 0

    while i < len(text):
        if text[i:i+5] == "s. r.":
            result.append("s. r.")
            i += 5
            result.append(" o.")
            i += 3
        else:
            result.append(text[i])
            i += 1

    return "".join(result)
