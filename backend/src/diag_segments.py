
import sys
from pathlib import Path

# Add backend/src to sys.path
backend_src = Path(r"c:\dev\saas-personalization\backend\src")
sys.path.append(str(backend_src))

from services.ml.predictor import get_segments

if __name__ == "__main__":
    try:
        segments = get_segments()
        import json
        print(json.dumps(segments, indent=2))
    except Exception as e:
        print(f"Error: {e}")
