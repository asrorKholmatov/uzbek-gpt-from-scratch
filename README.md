# Uzbek GPT from scratch

O'zbek tilida kichik GPT modelini noldan qurish loyihasi (o'rganish maqsadida).

A learning project: building a small Uzbek-language GPT model from scratch.

## Tuzilma / Structure

- `scripts/` — ma'lumot yig'ish va tozalash skriptlari
- `data/` — yuklab olingan va tozalangan matnlar (gitga qo'shilmaydi)

## 1-qadam: Vikipediya ma'lumotlarini yig'ish

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_wikipedia.py --limit 1000   # avval kichik sinov
python scripts/download_wikipedia.py                # to'liq
```

Natija `data/clean/wiki_uz.txt` fayliga yoziladi. Skript:
- kirill yozuvidagi matnni lotinchaga o'giradi, ruscha matnni tashlaydi;
- oʻ / gʻ dagi har xil apostroflarni (`' ‘ ’ \``) bitta `ʻ` belgiga keltiradi;
- "Manbalar", "Havolalar" kabi bo'limlarni, juda qisqa satr va maqolalarni olib tashlaydi;
- takroriy maqolalarni o'chiradi.

Testlar: `pip install pytest && cd scripts && python -m pytest`
