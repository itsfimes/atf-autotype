import re

def correct_text(text: str) -> str:
    text = replace_common_incorrect_characters(text)
    text = correct_spaces(text)
    return text


def replace_common_incorrect_characters(text: str) -> str:
    return text.replace("\n", " ").replace("|", "").replace("0", "o").replace("£", "f").replace(" ,", ",")


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
