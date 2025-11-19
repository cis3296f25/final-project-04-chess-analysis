from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .utils import get_stockfish_path
import chess
import chess.pgn
import chess.engine
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# Create your views here.
def home(request):
    # TODO: Move logic to upload.html view
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def analyze_game_stockfish(pgn_text):
    print("Starting Stockfish analysis...")
    # Automatically detect and get stockfish path
    stockfish_path = get_stockfish_path()
    
    # parse pgn
    from io import StringIO
    pgn = StringIO(pgn_text)
    game = chess.pgn.read_game(pgn)
    
    if not game:
        print("ERROR: Could not parse PGN!")
        return []
    
    print("PGN parsed successfully!")
    
    #initialize stockfish
    try:
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    except FileNotFoundError:
        print(f"ERROR: Stockfish not found at {stockfish_path}")
        return []
    
    analysis = []
    board = game.board()
    move_count = 0
    
    for move in game.mainline_moves():
        move_count += 1
       #  print(f"Analyzing move {move_count}...")
        
        #Analyze position (0.1 seconds per move)
        info = engine.analyse(board, chess.engine.Limit(time=0.1))
        score = info['score'].relative.score(mate_score=10000)
        
        # Convert centipawns to pawns
        evaluation = score / 100 if score else 0
        
        analysis.append({
            'move': board.san(move),
            'evaluation': evaluation
        })
        
        board.push(move)
    
    engine.quit()
    print(f"Analysis complete! Analyzed {len(analysis)} moves")
    
    return analysis


def upload(request):
    if request.method == 'POST' and request.FILES.get('pgn_file'):
        uploaded_file = request.FILES['pgn_file']

        # Save to /media/
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        # (Optional) Access the file path on backend:
        file_path = fs.path(filename)
        print(f"Saved at: {file_path}")

        # You can open/read it here if you want:
        with open(file_path, 'r') as f:
            content = f.read()
            analysis = analyze_game_stockfish(content)
        request.session["display"] = analysis
        analysis_print = analysis

        # Print analysis to console
        if analysis_print:
            print("\n" + "=" * 50)
            print("CHESS GAME ANALYSIS")
            print("=" * 50)
            for i, move_data in enumerate(analysis_print, 1):
                print(f"Move {i}: {move_data['move']}")
                print(f"  Evaluation: {move_data['evaluation']:.2f}")
                print("-" * 50)
            print("=" * 50 + "\n")

        request.session.modified = True
        print("Analysis saved to session: ", request.session.get("display"))
        return redirect("display")
    return render(request, 'upload.html')

def display(request):
    # TODO: Implement more robust analysis view (especially for graphs)
    analysis_result = request.session.get("display")
    if analysis_result is None:
        print("No analysis found in session. Redirecting to upload page.")
        return redirect("upload")
    else:
        print("Analysis found in session: ", analysis_result)

    paginator = Paginator(analysis_result, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "display.html", {"page_obj": page_obj})

def advantage_graph(request):
    # Get analysis from session (same data used in display())
    analysis_result = request.session.get("display")

    # X-axis: move numbers 1..N
    moves = list(range(1, len(analysis_result) + 1))
    # Y-axis: evaluation values in pawns
    evaluations = [item["evaluation"] for item in analysis_result]

    # Create the plot
    plt.figure(figsize=(10, 4))
    plt.plot(moves, evaluations)
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