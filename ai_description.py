import os
from itertools import cycle
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
keys = [v for k, v in os.environ.items() if k.startswith("OPENROUTER_API_KEY")]
if not keys:
    raise RuntimeError("Нет ни одного OPENROUTER_API_KEY в окружении")

# Создаём итератор по кругу
key_cycle = cycle(keys)

def get_client():
    key = next(key_cycle)
    return OpenAI(
        api_key=key,
        base_url="https://openrouter.ai/api/v1"
    )

def generate_description(name, brand):
    system_msg = {
        "role": "system",
        "content": (
            "Tu esi reklāmas tekstu autors latviešu valodā. "
            "Atbildi precīzi šādi:\n"
            "1. Īsais: <viena teikuma, līdz 10 vārdiem>\n"
            "2. Garais: <dažas rindkopas + punkti ar `- `>\n"
            "Bez HTML, bez liekas Markdown sintakses."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"Ģenerē aprakstu produktam «{name}» no zīmola «{brand}»."
    }

    for _ in range(len(keys)):
        client = get_client()
        try:
            resp = client.chat.completions.create(
                model="deepseek/deepseek-prover-v2:free",
                messages=[system_msg, user_msg],
                temperature=0.7,
                max_tokens=1024
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            continue
    return f"(Apraksta ģenerēšanas kļūda: {name})"
