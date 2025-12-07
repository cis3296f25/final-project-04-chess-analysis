import os
import platform
import shutil
from django.conf import settings

def get_stockfish_path():
    # Get the path to Stockfish.

    # 1. If project settings specify a custom path, use it.
    custom = getattr(settings, "STOCKFISH_PATH", None)
    if custom and os.path.exists(custom):
        return custom

    # 2. If user added Stockfish to PATH, use it.
    found = shutil.which("stockfish")
    if found:
        return found

    system = platform.system()

    # 3. OS-specific default installation locations.
    possible_paths = []

    if system == "Windows":
        local = os.getenv("LOCALAPPDATA", "")
        program = os.getenv("PROGRAMFILES", "")
        user = os.path.expanduser("~")

        possible_paths += [
            os.path.join(local, "Stockfish", "stockfish.exe"),
            os.path.join(program, "Stockfish", "stockfish.exe"),
            os.path.join(user, "stockfish", "stockfish.exe"),
            os.path.join(user, "stockfish", "stockfish-windows-x86-64-avx2.exe"),
        ]

    elif system == "Darwin":  # macOS
        possible_paths += [
            "/usr/local/bin/stockfish",
            "/opt/homebrew/bin/stockfish",
            "/Applications/Stockfish.app/Contents/MacOS/stockfish",
        ]

    else:  # Linux
        possible_paths += [
            "/usr/bin/stockfish",
	    "/home/ec2-user/final-project-04-chess-analysis/stockfish",
            "/usr/local/bin/stockfish",
            os.path.expanduser("~/stockfish/stockfish"),
        ]

    # Check each default location
    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 4. Final fallback error
    raise FileNotFoundError(
        "Could not find Stockfish. Please install it locally.\n"
        "Download: https://stockfishchess.org/download/"
    )
