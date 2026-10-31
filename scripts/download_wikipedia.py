"""O'zbek Vikipediyasini yuklab olib, tozalab, bitta matn fayliga yozadi.

Ishlatish:
    pip install -r requirements.txt
    python scripts/download_wikipedia.py

Natija: data/clean/wiki_uz.txt  (maqolalar orasida bitta bo'sh qator)
"""

import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uz_text import clean_whitespace, to_uzbek_latin  # noqa: E402

# Maqola oxiridagi foydasiz bo'limlar: shu sarlavhadan keyingi hammasi kesiladi
TAIL_SECTIONS = {
    "manbalar", "havolalar", "tashqi havolalar", "adabiyotlar",
    "izohlar", "yana qarang", "adabiyot", "manba",
}


def clean_article(text: str, min_line_chars: int):
    text = to_uzbek_latin(text)
    if text is None:
        return None
    kept = []
    for line in text.split("\n"):
        s = line.strip()
        if s.lower().rstrip(":") in TAIL_SECTIONS:
            break
        # Juda qisqa satrlar (sarlavhalar, ro'yxat qoldiqlari) olib tashlanadi
        if len(s) < min_line_chars:
            continue
        kept.append(s)
    return clean_whitespace("\n".join(kept))


def iter_articles(dataset_config: str, limit):
    from datasets import load_dataset

    ds = load_dataset("wikimedia/wikipedia", dataset_config, split="train")
    for i, row in enumerate(ds):
        if limit and i >= limit:
            break
        yield row["text"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="20231101.uz", help="HuggingFace konfiguratsiyasi")
    p.add_argument("--out", default="data/clean/wiki_uz.txt")
    p.add_argument("--min-article-chars", type=int, default=200,
                   help="Bundan qisqa maqolalar tashlanadi (bot yaratgan qisqa maqolalar ko'p)")
    p.add_argument("--min-line-chars", type=int, default=20)
    p.add_argument("--limit", type=int, default=0, help="Sinash uchun: faqat N ta maqola")
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    seen = set()
    stats = dict(total=0, kept=0, short=0, not_uz=0, dup=0, chars=0)

    with open(args.out, "w", encoding="utf-8") as f:
        for raw in iter_articles(args.config, args.limit):
            stats["total"] += 1
            text = clean_article(raw, args.min_line_chars)
            if text is None:
                stats["not_uz"] += 1
                continue
            if len(text) < args.min_article_chars:
                stats["short"] += 1
                continue
            h = hashlib.md5(text.encode("utf-8")).hexdigest()
            if h in seen:
                stats["dup"] += 1
                continue
            seen.add(h)
            f.write(text + "\n\n")
            stats["kept"] += 1
            stats["chars"] += len(text)
            if stats["total"] % 20000 == 0:
                print(f"  {stats['total']} ta maqola ko'rildi...")

    size_mb = os.path.getsize(args.out) / 1e6
    print(f"Jami maqola:        {stats['total']}")
    print(f"Saqlandi:           {stats['kept']}")
    print(f"Juda qisqa:         {stats['short']}")
    print(f"O'zbekcha emas:     {stats['not_uz']}")
    print(f"Takroriy:           {stats['dup']}")
    print(f"Fayl: {args.out}  ({size_mb:.1f} MB, {stats['chars']:,} belgi)")


if __name__ == "__main__":
    main()
