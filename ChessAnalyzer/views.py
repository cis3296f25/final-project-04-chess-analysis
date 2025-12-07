from django.shortcuts import render
from .chess_com_functions import lookup_elo, save_games
from .lichess_functions import lookup_elo_lichess
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.conf import settings
from .utils import get_stockfish_path
from ChessAnalyzer.engine import get_engine
from django.core.files.storage import default_storage
import chess
import chess.pgn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def home(request):
    # TODO: Move logic to upload.html view
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def analyze_game_stockfish(pgn_text):
    print("Starting Stockfish analysis...")
    singleton_engine = get_engine()
    engine = chess.engine.SimpleEngine.popen_uci(get_stockfish_path())
   

    # parse pgn
    from io import StringIO
    pgn = StringIO(pgn_text)

    all_games = []
    game_index =0
    
    while True:
        game = chess.pgn.read_game(pgn)
        if not game:
            break
        game_index+=1
        
            
        print(f"\nAnalyzing game #{game_index}..")
        

        analysis = []
        board = game.board()
        move_count = 0
    
        for move in game.mainline_moves():
            move_count += 1
            # Generate SAN safely
            try:
               if board.is_legal(move):
                  san=board.san(move)
               else:
                  san = move.uci()
            except (ValueError, AssertionError):
                san = move.uci()  # fallback to UCI if SAN fails)
            
            board.push(move)
            # THIS IS THE FIXED VERSION — works 100% with global engine
            info = engine.analyse(board, chess.engine.Limit(time=0.015))
            score = info.get("score")
            if score is not None:
                cp = score.relative.score(mate_score=10000)
                evaluation = round(cp / 100.0, 2) if cp is not None else None
            else:
                evaluation = None
            engine.configure({"Threads": 6})
            analysis.append({
                "move": san,
                "evaluation": evaluation,
            })

        all_games.append({
            "game_number": game_index,
            "moves": analysis
        })

    #print(f"Analysis complete! Analyzed {len(analysis)} moves")
    engine.quit()    
    return all_games


def upload(request):
    if request.method == 'POST' and request.FILES.get('pgn_file'):
        uploaded_file = request.FILES['pgn_file']

        # Save to /media/
        fs = default_storage
        filename = fs.save(f"uploaded/{uploaded_file.name}", uploaded_file)
        file_url = fs.url(filename)

        print(f"Saved at: {file_url}")

        # You can open/read it here if you want:
        with default_storage.open(filename, 'r') as f:
            content = f.read()
            analysis = analyze_game_stockfish(content)
        request.session["games"] = analysis
        analysis_print = analysis

        # Print analysis to console 
        # if analysis_print:
        #     print("\n" + "=" * 50)
        #     print("MULTI-GAME CHESS ANALYSIS")
        #     print("=" * 50)

        #     for game in analysis_print:
        #         print(f"\nGame #{game['game_number']}")
        #         print("-" * 40)
        #         for i, move_data in enumerate(game["moves"], 1):
        #             print(f"Move {i}: {move_data['move']}")
        #             print(f"  Evaluation: {move_data['evaluation']:.2f}")

        #     print("=" * 50 + "\n")


        request.session.modified = True
        print("Analysis saved to session: ", request.session.get("display"))
        return redirect("display")
    return render(request, 'upload.html')

def display(request):
    games = request.session.get("games")
    if not games:
        return redirect("upload")

    game_number = int(request.GET.get("game", 1))
    if game_number < 1 or game_number > len(games):
        game_number = 1

    selected_game = games[game_number - 1]["moves"]

    paginator = Paginator(selected_game, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "display.html", {
    "page_obj": page_obj,
    "current_game": game_number,
    "game_list": list(range(1, len(games) + 1))
    })

def analyze_online(request):
    """
    Analyze a Chess.com username using lookup_elo.
    """
    context = {}

    if request.method == "POST":
        action = request.POST.get("action")
        username = request.POST.get("username")
        platform = request.POST.get("platform") # Chess.com or Lichess
        if action == "lookup":
            if username:
                if platform == "Chess.com":
                    stats, error = lookup_elo(username)
                else:
                    username = username.lower()
                    stats, error = lookup_elo_lichess(username)
                if error:
                    context["error"] = error
                else:
                    context["stats"] = stats
                    context["username"] = username
                    context["platform"] = platform
        elif action == "load_games":
            n = int(request.POST.get("count", 10))
            if username:
                if platform == "Chess.com":
                    print("TODO")
                else:
                    username = username.lower()
                    stats, error = lookup_elo_lichess(username)

            


    return render(request, "analyze_online.html", context)



def advantage_graph(request):
    games = request.session.get("games")
    game_number = int(request.GET.get("game", 1))
    if not games:
        return redirect("upload")
    selected_game = games[game_number - 1]["moves"]

    moves = list(range(1, len(selected_game) + 1))
    evaluations = [item["evaluation"] for item in selected_game]
    # Create the plot
    plt.figure(figsize=(17, 4))
    plt.plot(moves, evaluations)
    plt.ylim(-105, 105)
    plt.axhline(0, linestyle='--', linewidth=1)  # zero line at 0
    plt.xlabel("Move number")
    plt.ylabel("Evaluation (pawns, + = White, - = Black)")
    plt.title("Advantage Over Time")
    plt.tight_layout()

    # Save the plot into MEDIA_ROOT
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)  # ensure folder exists
    plot_path = os.path.join(settings.MEDIA_ROOT, "advantage.png")
    plt.savefig(plot_path)
    plt.close()

    # Build URL to serve the image
    plot_url = settings.MEDIA_URL + "advantage.png"

    # Render template that just shows the image
    return render(request, "advantage_graph.html", {"plot_url": plot_url})
