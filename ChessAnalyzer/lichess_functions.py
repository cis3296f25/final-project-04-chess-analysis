import requests, time, os

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