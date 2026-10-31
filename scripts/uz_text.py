"""O'zbek matnini tozalash uchun yordamchi funksiyalar.

Asosiy vazifalar:
  1. Kirill yozuvidagi o'zbek matnini lotinchaga o'girish.
  2. oʻ / gʻ va tutuq belgisidagi har xil apostroflarni bittaga keltirish.
  3. Matn haqiqatan o'zbekchami yoki yo'qligini taxminan aniqlash.
"""

import re
import unicodedata

# oʻ va gʻ uchun rasmiy belgi: U+02BB (ʻ). Tutuq belgisi: U+02BC (ʼ).
OKINA = "ʻ"
TUTUQ = "ʼ"
# Odamlar yozadigan har xil "apostrof"lar
APOSTROPHES = "'`‘’ʻʼʹ´"

# --- Kirill -> Lotin --------------------------------------------------------
CYR2LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ж": "j", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "x",
    "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh", "ъ": TUTUQ, "ь": "",
    "ы": "i", "э": "e", "ё": "yo", "ю": "yu", "я": "ya",
    "ў": "o" + OKINA, "қ": "q", "ғ": "g" + OKINA, "ҳ": "h",
}
VOWELS_CYR = set("аеёиоуўэюяАЕЁИОУЎЭЮЯ")
UZ_ONLY_CYR = set("ўқғҳЎҚҒҲ")   # faqat o'zbek kirillida bor harflar
CYR_RE = re.compile(r"[Ѐ-ӿ]")


def _translit_char(ch: str, prev: str) -> str:
    low = ch.lower()
    if low == "е":
        # So'z boshida yoki unlidan keyin "ye", aks holda "e"
        out = "ye" if (not prev or not prev.isalpha() or prev in VOWELS_CYR) else "e"
    elif low in CYR2LAT:
        out = CYR2LAT[low]
    else:
        return ch
    if ch != low and out:  # katta harf
        out = out[0].upper() + out[1:]
    return out


def cyr_to_lat(text: str) -> str:
    """O'zbek kirill matnini lotinchaga o'giradi."""
    out = []
    prev = ""
    for ch in text:
        out.append(_translit_char(ch, prev))
        prev = ch
    return "".join(out)


# --- Apostroflar -----------------------------------------------------------
_OG_RE = re.compile(r"([oOgG])[" + re.escape(APOSTROPHES) + r"]")
_TUTUQ_RE = re.compile(r"(?<=\w)[" + re.escape(APOSTROPHES) + r"](?=\w)")


def normalize_apostrophes(text: str) -> str:
    """oʻ/gʻ -> U+02BB, so'z ichidagi boshqa apostroflar -> U+02BC (tutuq)."""
    text = _OG_RE.sub(lambda m: m.group(1) + OKINA, text)
    text = _TUTUQ_RE.sub(lambda m: m.group(0) if m.group(0) == OKINA else TUTUQ, text)
    return text


# --- Til / yozuvni aniqlash -------------------------------------------------
def cyrillic_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if CYR_RE.match(c)) / len(letters)


def to_uzbek_latin(text: str):
    """Matnni lotin o'zbekchaga keltiradi.

    Agar matn asosan kirillda bo'lsa-yu, unda o'zbekcha harflar (ў қ ғ ҳ)
    bo'lmasa, u katta ehtimol bilan ruscha — bunday holda None qaytaramiz.
    """
    text = unicodedata.normalize("NFC", text)
    if cyrillic_ratio(text) > 0.5:
        if not any(c in UZ_ONLY_CYR for c in text):
            return None
        text = cyr_to_lat(text)
    return normalize_apostrophes(text)


# --- Umumiy tozalash -------------------------------------------------------
_SPACES_RE = re.compile(r"[ \t ]+")
_MANY_NEWLINES_RE = re.compile(r"\n{3,}")


def clean_whitespace(text: str) -> str:
    text = _SPACES_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return _MANY_NEWLINES_RE.sub("\n\n", text).strip()
