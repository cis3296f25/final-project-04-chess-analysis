import requests, time, os
# from .views import analyze_game_stockfish

# returns two things (stats, error)
def lookup_elo_lichess(username):
    if not username:
        return None
    
    headers = {
    "User-Agent": "MyChessApp/1.0"
    }

    url = f"https://lichess.org/api/user/{username}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 404:
            return None, f"User '{username}' not found on Lichess."
        else:
            return None, f"Lichess API returned error {response.status_code}."
    
    data = response.json()

    stats = {
        "rapid": data.get("perfs", {}).get("rapid", {}).get("rating"),
        "blitz": data.get("perfs", {}).get("blitz", {}).get("rating"),
        "bullet": data.get("perfs", {}).get("bullet", {}).get("rating"),
        "classical": data.get("perfs", {}).get("classical", {}).get("rating")
    }

    return stats, None

def fetch_games(username, n):
    if not username:
        return None
    
    headers = {
    "User-Agent": "MyChessApp/1.0"
    }

    url = f"https://lichess.org/api/games/user/{username}?max={n}"

    response = requests.get(url, headers=headers)
    pgn_text = response.text
    
    print(pgn_text)

    # with open(f"{username}_last_{n}_games.pgn", "w", encoding="utf-8") as f:
    #     f.write(pgn_text)

    return pgn_text, None