from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path(sys.argv[0]).resolve().parent