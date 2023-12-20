import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sibling_dir = os.path.join(current_dir, "..", "static")
sys.path.append(sibling_dir)
