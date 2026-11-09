# sourced by every script: sets HERE (project folder), BL (Blender 5.x path), PY (system python) and nat() (native path).
# Works in Git Bash on Windows and plain bash on Linux (e.g. a RunPod pod). Override with BLENDER=/path/to/blender, PYTHON=python3.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "$BLENDER" ]; then BL="$BLENDER"
else
  BL="$(ls -d "/c/Program Files/Blender Foundation/Blender 5."*/blender.exe 2>/dev/null | sort -V | tail -1)"
  [ -n "$BL" ] || BL="$(ls -d /workspace/blender/blender /workspace/blender-5.*/blender /opt/blender-5.*/blender "$HOME"/blender-5.*/blender 2>/dev/null | sort -V | tail -1)"
  [ -n "$BL" ] || BL="$(command -v blender)"
fi
[ -x "$BL" ] || { echo "Blender 5.x not found. Install it or set BLENDER=/path/to/blender"; exit 1; }
if [ -n "$PYTHON" ]; then PY="$PYTHON"; elif command -v python3 >/dev/null && python3 -c '' 2>/dev/null; then PY=python3; else PY=python; fi
export PYTHON="$PY"
# native path of the current folder: C:/... in Git Bash (Blender is a Windows program), plain path elsewhere
nat() { pwd -W 2>/dev/null || pwd; }
