import os
import json

LANG: str = os.getenv("language", "CN")
translation: dict[str, str]

if LANG not in ['CN', 'EN']:
    raise ValueError(f"Unsupported language: {LANG}")

if LANG == 'EN':
    with open('translation.json', 'r', encoding='utf-8') as f:
        translation = json.load(f)

def i18n(key: str) -> str:
    if LANG == 'CN':
        return key
    return translation.get(key, key)
