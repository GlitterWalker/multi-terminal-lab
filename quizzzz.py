import os
import re
import sys
import time
import json
import readline  # noqa: F401 - makes backspace / arrow keys work in input()

import boto3

BUCKET_NAME = os.environ.get("BUCKET_NAME", "lab-leaderboard")
BOARD_URL = os.environ.get("BOARD_URL", "")
TIME_LIMIT = 900  # seconds
DONE_FILE = "/home/student/.done"

GREEN, RED, YELLOW, CYAN, BOLD, END = (
    "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m")
PROMPT = "\001\033[92m\002$\001\033[0m\002 "  # colour-safe prompt for readline

# State checks (silent). NOTE: no 'docker images | grep REPOSITORY' - new Docker
# versions changed that output, so we use -q / inspect instead.
EXISTS = "test -n \"$(docker ps -aq -f 'name=^mynginx$')\""
RUNNING = "test -n \"$(docker ps -q -f 'name=^mynginx$')\""
GONE = "test -z \"$(docker ps -aq -f 'name=^mynginx$')\""
NO_EXITED = "test -z \"$(docker ps -aq -f status=exited)\""

# pat   = regex the typed command must match (None = any command)
# check = shell test on the resulting state (None = pattern alone is enough)
questions = [
    {"q": "Create a file named file.txt", "pat": None,
     "check": "test -f file.txt", "hint": "touch <filename>"},
    {"q": "Delete file.txt", "pat": r"\brm\b",
     "check": "test ! -f file.txt", "hint": "rm <filename>"},
    {"q": "Create a directory named testdir", "pat": r"\bmkdir\b",
     "check": "test -d testdir", "hint": "mkdir <dirname>"},
    {"q": "Remove the directory testdir", "pat": r"\b(rmdir|rm)\b",
     "check": "test ! -d testdir", "hint": "rmdir <dirname>  (or rm -r)"},
    {"q": "Show the current directory", "pat": r"^\s*pwd\b",
     "check": None, "hint": "Print Working Directory (3 letters)"},
    {"q": "List the files here", "pat": r"^\s*(ls|ll|dir)\b",
     "check": None, "hint": "ls"},
    {"q": "Create a file named hello.txt", "pat": None,
     "check": "test -f hello.txt", "hint": "touch <filename>"},
    {"q": "Show docker images", "pat": r"^\s*docker\s+(images|image\s+(ls|list))\b",
     "check": None, "hint": "docker images"},
    {"q": "Pull the nginx image", "pat": r"^\s*docker\s+(image\s+)?pull\s+nginx\b",
     "check": "docker image inspect nginx", "hint": "docker pull <image>"},
    {"q": "Run an nginx container named mynginx in the background",
     "pat": r"^\s*docker\s+(container\s+)?run\b", "check": RUNNING,
     "hint": "docker run -d --name <name> <image>   (-d = background)"},
    {"q": "Stop the mynginx container",
     "pat": r"^\s*docker\s+(container\s+)?stop\b",
     "check": EXISTS + " && ! " + RUNNING, "hint": "docker stop <name>"},
    {"q": "Remove the mynginx container",
     "pat": r"^\s*docker\s+(container\s+)?rm\b", "check": GONE,
     "hint": "docker rm <name>"},
    {"q": "Run the nginx container named mynginx again (background)",
     "pat": r"^\s*docker\s+(container\s+)?run\b", "check": RUNNING,
     "hint": "docker run -d --name <name> <image>"},
    {"q": "List ALL containers, including stopped ones",
     "pat": r"^\s*docker\s+(ps|container\s+ls)\s+.*(-\w*a\w*|--all)",
     "check": None, "hint": "docker ps with the -a flag"},
    {"q": "Remove all stopped containers",
     "pat": r"^\s*docker\s+(container\s+prune|rm\b)", "check": NO_EXITED,
     "hint": "docker container prune   (answer y)"},
]


def fmt(s):
    s = max(0, int(s))
    return f"{s // 60:02d}:{s % 60:02d}"


def run(cmd):
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print()


def check_ok(check):
    return os.system("( " + check + " ) >/dev/null 2>&1") == 0


def main():
    if os.path.exists(DONE_FILE):
        print(f"{YELLOW}You already finished this lab. Thanks for playing!{END}")
        if BOARD_URL:
            print(f"Leaderboard: {CYAN}{BOARD_URL}{END}")
        return

    name = os.environ.get("STUDENT_NAME", "").strip()
    while not name:
        name = input("Enter your name: ").strip()

    os.system("clear")
    print(f"{BOLD}{CYAN}Linux + Docker Lab{END}")
    print(f"Hi {BOLD}{name}{END}! {len(questions)} tasks, {TIME_LIMIT // 60} minutes.\n")
    print("How it works:")
    print("  - Type a real shell command that completes the task")
    print("    (not the answer in words). It runs, then the result is checked.")
    print(f"  - {BOLD}hint{END} = a clue    {BOLD}skip{END} = move to the next task")
    print("  - For Docker tasks, use -d so containers run in the background.")
    try:
        input(f"\n{YELLOW}Press Enter to start the timer...{END}")
    except EOFError:
        return

    start = time.time()
    score = skipped = 0
    timed_out = False

    for i, item in enumerate(questions, 1):
        left = TIME_LIMIT - (time.time() - start)
        if left <= 0:
            timed_out = True
            break
        print(f"\n{BOLD}{CYAN}Q{i}/{len(questions)}{END}  {BOLD}{item['q']}{END}")
        print(f"{YELLOW}score {score} | skipped {skipped} | {fmt(left)} left{END}")

        while True:
            if time.time() - start > TIME_LIMIT:
                timed_out = True
                break
            try:
                cmd = input(PROMPT).strip()
            except KeyboardInterrupt:
                print("\n(type 'skip' to skip this task)")
                continue
            except EOFError:
                sys.exit(0)

            low = cmd.lower()
            if not cmd:
                continue
            if low == "skip":
                print(f"{YELLOW}Skipped.{END}")
                skipped += 1
                break
            if low == "hint":
                print(f"{YELLOW}Hint: {item['hint']}{END}")
                continue

            run(cmd)

            if item["pat"] and not re.search(item["pat"], cmd):
                print(f"{RED}That's not the command for this task.{END} "
                      f"Type {BOLD}hint{END} for a clue or {BOLD}skip{END}.")
                continue
            if item["check"] is None or check_ok(item["check"]):
                print(f"{GREEN}Correct!{END}")
                score += 1
                break
            print(f"{RED}Command ran, but the task isn't done yet.{END} "
                  f"Try again, {BOLD}hint{END} or {BOLD}skip{END}.")

        if timed_out:
            break

    elapsed = int(min(time.time() - start, TIME_LIMIT))
    print(f"\n{BOLD}{'Time is up!' if timed_out else 'Quiz completed!'}{END}")
    print(f"Score: {BOLD}{score}/{len(questions)}{END}   "
          f"Skipped: {skipped}   Time: {fmt(elapsed)}")

    result = {"name": name, "score": score, "total": len(questions),
              "skipped": skipped, "time": elapsed}
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", name)[:30] or "student"
    file_name = f"{safe}_{int(time.time())}.json"
    local_path = f"/tmp/{file_name}"
    with open(local_path, "w") as f:
        json.dump(result, f)

    try:
        boto3.client("s3").upload_file(local_path, BUCKET_NAME, file_name)
        print(f"{GREEN}Result uploaded to the leaderboard.{END}")
        try:
            open(DONE_FILE, "w").close()
        except OSError:
            pass
    except Exception as e:
        print(f"{RED}Upload failed: {e}{END}")

    if BOARD_URL:
        print(f"Leaderboard: {CYAN}{BOARD_URL}{END}")
    print("You can close this tab.")


if __name__ == "__main__":
    main()
