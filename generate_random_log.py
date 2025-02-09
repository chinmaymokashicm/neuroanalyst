"""
Simple script to write streaming logs to a file
"""
import time, random
from pathlib import Path

log_file = Path("logs/app.log")
log_type: list[str] = ["INFO", "WARNING", "ERROR"]

while True:
    with open(log_file, "a") as f:
        random_log_type = random.choice(log_type)
        log = f"{random_log_type}: This is a random log message<br>"
        color: str = "red" if random_log_type == "ERROR" else "orange" if random_log_type == "WARNING" else "black"
        log = f"<span style='color:{color}'>{log}</span>"
        f.write(log)
        print(log)
    time.sleep(0.5)