import re
import difflib
import unicodedata

autocorrect_dict = {
    "Kanil": "Kamil",
    "Hanr": "Hamr",
    "důn": "dům",
    "notel": "motel"
}


def correct_text(text: str, autocorrect_db: list[str] | None = None) -> str:
    text = autocorrect(replace_common_incorrect_characters(text), autocorrect_dict)
    text = fix_comma_spaces(correct_spaces(text))
    text = fix_casing(fix_lowercase_letters(text))
    print(text)
    if autocorrect_db:
        text = correct_big_text(text, autocorrect_db, 0.8)
    return text


def replace_common_incorrect_characters(text: str) -> str:
    return text.replace("\n", " ").replace("|", "").replace("0", "o").replace("£", "f").replace(" ,", ",")

def fix_lowercase_letters(text: str) -> str:
    if not len([c for c in text if c.isupper()]) > 2:
        return text.lower()
    return text

def fix_casing(text: str) -> str:
    text_split: list[str] = text.split()
    for idx, word in enumerate(text_split):
        if not word[1:].islower():
            text_split[idx] = f"{word[0]}{word[1:].lower()}"
    return " ".join(text_split)

def fix_comma_spaces(text: str) -> str:
    return text.replace(",", ", ")

def correct_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text)

def autocorrect(text: str, autocorrect_dict: dict[str, str]) -> str:
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, autocorrect_dict.keys())) + r")\b")

    return pattern.sub(lambda m: autocorrect_dict[m.group(0)], text)

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

def normalize(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))

def tokenize_with_positions(s: str):
    # yields (word, start, end)
    for m in re.finditer(r"\w+", s, flags=re.UNICODE):
        yield m.group(), m.start(), m.end()

def ngrams_with_positions(tokens, min_n=2, max_n=4):
    for n in range(min_n, max_n + 1):
        for i in range(len(tokens) - n + 1):
            words = tokens[i:i+n]
            text = " ".join(w[0] for w in words)
            start = words[0][1]
            end = words[-1][2]
            yield text, start, end

def expand_to_separators(text, start, end):
    while start > 0 and text[start - 1] in " \n,":
        start -= 1
    while end < len(text) and text[end] in " \n,":
        end += 1
    return start, end


def correct_big_text(big_text: str, choices: list[str], threshold=0.8) -> str:
    return big_text
    normalized_text = normalize(big_text)


    result = []
    buffer = ""
    i = 0

    while i < len(normalized_text):
        buffer += normalized_text[i]

        match = closest_match(buffer, choices)
        if match:
            norm_match = normalize(match)

            ratio = difflib.SequenceMatcher(None, buffer, norm_match).ratio()
            length_close = abs(len(buffer) - len(norm_match)) <= 1

            if ratio >= threshold and length_close:
                # Commit the match
                result.append(match)
                buffer = ""
                i += 1
                continue

        # If buffer is getting too long without a good match, flush first char
        if len(buffer) > max(len(normalize(c)) for c in choices):
            result.append(buffer[0])
            buffer = buffer[1:]

        i += 1

    # Flush remaining buffer
    if buffer:
        result.append(buffer)

    return "".join(result).replace("\n", " ")

def closest_match(query: str, choices: list[str]) -> str | None:
    norm_choices = [(choice, normalize(choice)) for choice in choices]

    best = max(
        norm_choices,
        key=lambda item: difflib.SequenceMatcher(None, query, item[1]).ratio(),
        default=None
    )

    return best[0] if best else None
