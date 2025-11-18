import requests, time, os

# returns two things (stats, error)
def lookup_elo(username):
    if not username:
        return None
    
    headers = {
    "User-Agent": "MyChessApp/1.0"
    }

    url = f"https://api.chess.com/pub/player/{username}/stats"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 301:
            return None, "The Chess.com API endpoint has moved permanently (301)."
        elif response.status_code == 304:
            return None, "No new data available (304 Not Modified)."
        elif response.status_code == 403:
            return None, "Access forbidden — you may have hit a Chess.com rate limit (403)."
        elif response.status_code == 404:
            return None, f"User '{username}' not found on Chess.com (404)."
        elif response.status_code == 410:
            return None, "This resource is no longer available (410 Gone)."
        elif response.status_code == 429:
            return None, "Too many requests, you are being rate-limited by Chess.com (429)."
        else:
            return None, f"Unexpected error from Chess.com API ({response.status_code})."
    
    data = response.json()

    stats = {
        "rapid": data.get("chess_rapid", {}).get("last", {}).get("rating"),
        "blitz": data.get("chess_blitz", {}).get("last", {}).get("rating"),
        "bullet": data.get("chess_bullet", {}).get("last", {}).get("rating"),
    }

    return stats, None

def lookup_games(username):
    if not username:
        return None, "No username provided."
    
    headers = {
    "User-Agent": "MyChessApp/1.0"
    }

    arch_url = f"https://api.chess.com/pub/player/{username}/games/archives"

    response = requests.get(arch_url, headers=headers)

    if response.status_code != 200:
        error_messages = {
            301: "The Chess.com API endpoint has moved permanently (301).",
            304: "No new data available (304 Not Modified).",
            403: "Access forbidden.",
            404: f"User '{username}' not found on Chess.com (404).",
            410: "This resource is no longer available (410 Gone).",
            429: "Too many requests. You are being rate-limited by Chess.com (429)."
        }
        return None, error_messages.get(response.status_code, f"Unexpected error ({response.status_code}).")

    archives = response.json().get("archives", [])

    

    for url in archives[0]:
        year, month = url.split("/")[-2:]
        file_path = f"{username}_{year}_{month}.pgn"

        try:
            pgn_url = url + "/pgn"
            pgn_response = requests.get(pgn_url, headers=headers)

            if pgn_response.status_code == 200:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(pgn_response.text)
                print(f"✅ Saved: {file_path}")
            else:
                print(f"⚠️ Skipped {url} — status {pgn_response.status_code}")
        except:
            print()


        



    return None, None

# from django.shortcuts import render
# from ...chess_com_functions import lookup_elo, lookup_games

# # Create your views here.
# def home(request):
#     username = None # default username is None
#     elos = None
#     error = None

#     if request.method == "POST":
#         username = request.POST.get("username") # get username from form data
#         elos, error = lookup_games(username)

#     return render(request, 'home.html', {
#         "username": username,
#         "elos": elos,
#         "error": error
#         })