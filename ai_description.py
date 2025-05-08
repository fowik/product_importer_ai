import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

def generate_description(name, brand):
    prompt = f"""
Tu esi latviešu valodā rakstošs reklāmas tekstu autors. Uzraksti oriģinālu aprakstu produktam **{name}** no zīmola **{brand}** divās daļās:

1. Īss apraksts (1 teikums)
2. Detalizēts apraksts ar galvenajām īpašībām (punkts pa punktam)
    """

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        content = response.choices[0].message.content.strip()
        return content if content else f"(Apraksts nav pieejams: {name})"
    except Exception as e:
        print(f"⚠️ Kļūda ({name}): {e}")
        return f"(Apraksts kļūda: {name})"
