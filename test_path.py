import os
import sys
path = os.path.join(os.path.dirname(__file__), 'Guiones')
sys.path.append(path)
print(f"DEBUG: sys.path appended {path}")
try:
    import ia_paths
    print("DEBUG: import ia_paths SUCCESS")
    print(f"DEBUG: ia_paths file: {ia_paths.__file__}")
except Exception as e:
    print(f"DEBUG: import ia_paths FAILED: {e}")
