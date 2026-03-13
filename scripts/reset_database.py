from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from obuv_app.database import DatabaseManager


if __name__ == "__main__":
    manager = DatabaseManager()
    manager.reset()
    print("База данных заново создана и заполнена исходными данными.")
