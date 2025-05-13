import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def safe_request(url: str, timeout: int = 10) -> "requests.Response | None":
    """
    Making a GET request to the given URL with a timeout.
    If the request fails, it returns None and prints an error message.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        print(f"⚠️ Ошибка запроса {url}: {e}")
        return None
