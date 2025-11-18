from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils import get_stockfish_path
import chess
import chess.pgn
import chess.engine

# Create your views here.
def home(request):
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
        
        # Print analysis to console
        if analysis:
            print("\n" + "="*50)
            print("CHESS GAME ANALYSIS")
            print("="*50)
            for i, move_data in enumerate(analysis, 1):
                print(f"Move {i}: {move_data['move']}")
                print(f"  Evaluation: {move_data['evaluation']:.2f}")
                print("-"*50)
            print("="*50 + "\n")

        return render(request, 'home.html', {'analysis': analysis})
    return render(request, 'home.html')

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