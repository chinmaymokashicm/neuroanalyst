import subprocess
import pathlib

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    script = root / "set_envs.sh"
    subprocess.run(["bash", str(script)], check=True)
