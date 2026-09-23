import os
import time
import json
import boto3

BUCKET_NAME = "lab-leaderboard"

questions = [
    {"q": "Create a file named file.txt", "check": "test -f file.txt"},
    {"q": "Delete file.txt", "check": "test ! -f file.txt"},
    {"q": "Create a directory testdir", "check": "test -d testdir"},
    {"q": "Remove directory testdir", "check": "test ! -d testdir"},
    {"q": "Show current directory", "check": "pwd > /dev/null"},
    {"q": "List files", "check": "ls > /dev/null"},
    {"q": "Create file hello.txt", "check": "test -f hello.txt"},
    {"q": "Show docker images", "check": "docker images | grep -q REPOSITORY"},
    {"q": "Pull nginx image", "check": "docker images | grep -q nginx"},
    {"q": "Run nginx container with name mynginx", "check": "docker ps | grep -q mynginx"},
    {"q": "Stop nginx container", "check": "docker ps | grep -q mynginx && exit 1 || exit 0"},
    {"q": "Remove nginx container", "check": "docker ps -a | grep -q mynginx && exit 1 || exit 0"},
    {"q": "Run nginx container again", "check": "docker ps | grep -q mynginx"},
    {"q": "List all containers", "check": "docker ps -a | grep -q CONTAINER"},
    {"q": "Remove all stopped containers", "check": "docker ps -a --filter status=exited | grep -q . && exit 1 || exit 0"}
]

print("🔥 Terminal Lab Challenge")
print("👉 Type 'skip' to skip a question\n")

name = input("Enter your name: ")

start_time = time.time()
time_limit = 900
score = 0
skipped = 0

for i, item in enumerate(questions):
    print(f"\nQ{i+1}: {item['q']}")

    while True:
        if time.time() - start_time > time_limit:
            print("\n⏰ Time Up!")
            break

        cmd = input("$ ").strip()

        if cmd.lower() == "skip":
            print("⏭ Skipped!")
            skipped += 1
            break

        if cmd == "":
            continue

        os.system(cmd)

        result = os.system(item["check"])

        if result == 0:
            print("✅ Correct!")
            score += 1
            break
        else:
            print("❌ Try again (or type 'skip')")

    if time.time() - start_time > time_limit:
        break

end_time = time.time()

print("\n🎯 Quiz Completed")
print(f"Score: {score}/{len(questions)}")

# ✅ Create result JSON
result_data = {
    "name": name,
    "score": score,
    "total": len(questions),
    "skipped": skipped,
    "time": int(end_time - start_time)
}

# Save locally (optional)
file_name = f"{name}_{int(time.time())}.json"
local_path = f"/tmp/{file_name}"

with open(local_path, "w") as f:
    json.dump(result_data, f)

# 🔥 Upload to S3
s3 = boto3.client("s3")
s3.upload_file(local_path, BUCKET_NAME, file_name)

print(" Result uploaded to S3!")