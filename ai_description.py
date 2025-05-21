import os
from itertools import cycle
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
keys = [v for k, v in os.environ.items() if k.startswith("OPENROUTER_API_KEY")]
if not keys:
    raise RuntimeError("Нет ни одного OPENROUTER_API_KEY в окружении")

key_cycle = cycle(keys)

def get_client():
    key = next(key_cycle)
    return key, OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")

def generate_description(name, brand, max_retries=3):
    system_msg = {
        "role": "system",
        "content": (
            "Tu esi reklāmas tekstu autors latviešu valodā. "
            "Mēģini atbildēt šādā formā:\n"
            "1. Īsais: <viena teikuma, līdz 10 vārdiem>\n"
            "2. Garais: <dažas rindkopas + punkti ar `- `>\n"
            "Bez HTML, bez Markdown.\n\n"
            "Obligāti izmanto formātu: '1. Īsais:' un '2. Garais:', katrs no jaunas rindas."
            "Piemērs:\n"
            "1. Īsais: Eleganta tekstila moto jaka ar drošību un komfortu.\n"
            "2. Garais: Furygan 6002-1 Jack Glenn Black ir daudzpusīga motociklistu jaka, kas apvieno izturību, aizsardzību un diskrētu pilsētas stilu. Tā ir lieliski piemērota braucējiem, kuri meklē funkcionālu un stilīgu risinājumu ikdienas lietošanai.\n"
            "- CE sertificēti plecu un elkoņu aizsargi, ar vietu muguras aizsargam.\n"
            "- Izturīgs un elpojošs tekstilmateriāls – piemērots dažādiem laikapstākļiem.\n"
            "- Regulējami aproces, jostasvieta un apkakle – individuālam piegulumam.\n"
            "- Daudz kabatu un ērta iekšējā odere – praktiskums ikdienas braucienos.\n"
            "- Klasiski melns dizains – neuzkrītošs un elegants pilsētas stilam."
        )
    }

    user_msg = {
        "role": "user",
        "content": f"Ģenerē aprakstu produktam «{name}» no zīmola «{brand}»."
    }

    models = [
        "deepseek/deepseek-prover-v2:free",
        "mistralai/mistral-7b-instruct:free"
    ]

    for _ in range(max_retries):
        for model in models:
            for _ in range(len(keys)):
                key, client = get_client()
                try:
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[system_msg, user_msg],
                        temperature=0.7,
                        max_tokens=1024
                    )
                    content = resp.choices[0].message.content.strip() if resp.choices else None
                    if content:
                        return content
                    else:
                        print(f"[WARN] Пустой ответ от модели {model} с ключом {key[:8]}...")
                except Exception as e:
                    print(f"[ERROR] {model} — ключ {key[:8]}... — {type(e).__name__}: {e}")
    return f"(Apraksta ģenerēšanas kļūda: {name})"

