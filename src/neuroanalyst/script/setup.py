import subprocess
import pathlib

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    script = root / "setup.sh"
    subprocess.run(["bash", str(script)], check=True)
