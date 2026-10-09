"""Engine Gaming: new contracts over the unchanged pinned research engine."""
from pathlib import Path
import sys
SOURCE = Path(__file__).resolve().parents[1] / 'vendor' / 'socionics'
if not (SOURCE/'hle_unified').is_dir():
    raise ImportError('Run git submodule update --init --recursive first')
for root in (SOURCE, SOURCE/'baseline'/'HLE_Rebuild_R21B'):
    if str(root) not in sys.path: sys.path.append(str(root))
