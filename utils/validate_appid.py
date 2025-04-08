import requests


def validate_game(gameid: int) -> bool:
    url = f"https://store.steampowered.com/app/{gameid}?cc=us&l=en"
    cookies = {
        "wants_mature_content": "1",
        "birthtime": "189302401",
        "lastagecheckage": "1-January-1976",
    }

    try:
        response = requests.get(url, cookies=cookies, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
