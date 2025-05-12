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
    prompt = f"""
Tu esi latviešu valodā rakstošs reklāmas tekstu autors. Uzraksti oriģinālu aprakstu produktam **{name}** no zīmola **{brand}** divās daļās:

1. Īss apraksts (1 teikums, līdz 10 vārdiem )
2. Detalizēts apraksts ar galvenajām īpašībām (teksts par produktu + punkts pa punktam)
""".strip()

    # Попробуем получить ответ, перебирая ключи до успеха или исчерпания пула
    for _ in range(len(keys)):
        client = get_client()
        try:
            resp = client.chat.completions.create(
                model="deepseek/deepseek-prover-v2:free",
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.choices[0].message.content.strip()
            return text or f"(Apraksts nav pieejams: {name})"
        except Exception as e:
            print(f"⚠️ Ошибка с ключом, пробуем следующий: {e}")
            continue

    # Если все ключи упали
    return f"(Apraksts kļūda: {name})"