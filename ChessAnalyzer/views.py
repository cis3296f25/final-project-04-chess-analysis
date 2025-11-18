from django.shortcuts import render
from ..chess_com_functions import lookup_elo, lookup_games

# Create your views here.
def home(request):
    username = None # default username is None
    elos = None
    error = None

    if request.method == "POST":
        username = request.POST.get("username") # get username from form data
        elos, error = lookup_games(username)

    return render(request, 'home.html', {
        "username": username,
        "elos": elos,
        "error": error
        })