from flask import Flask, request, jsonify
from pages import HOME_HTML, BOARD_HTML
from flask import Response
import uuid
import subprocess
import time
import os
import boto3
import json

app = Flask(__name__)

# 🔧 CONFIG
BASE_PORT = 8000
EC2_IP = "13.235.86.32"
BUCKET_NAME = "lab-leaderboard1"

sessions = {}

# 📂 Local results directory
RESULTS_DIR = os.path.join(os.getcwd(), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


#  Check if port is free (FIXES ttyd crash)
def is_port_free(port):
    result = subprocess.run(
        ["lsof", "-i", f":{port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode != 0


def get_free_port():
    port = BASE_PORT
    while True:
        if is_port_free(port):
            return port
        port += 1


# 🔹 Home
@app.route("/")
def home():
    return Response(HOME_HTML, mimetype="text/html")


@app.route("/board")
def board():
    return Response(BOARD_HTML, mimetype="text/html")


# 🔹 Start Lab
@app.route("/start", methods=["POST"])
def start_lab():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()[:30]

    if not name:
        return jsonify({"error": "Name required"}), 400

    session_id = str(uuid.uuid4())[:8]
    container_name = f"user_{session_id}"
    port = get_free_port()

    try:
        # 🚀 Run container
        subprocess.run([
            "docker", "run", "-dit",
            "--name", container_name,
            "--user", "root",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "-v", f"{RESULTS_DIR}:/home/student/results",
            "lab-image"
        ], check=True)

        #  Start terminal (ttyd)
        subprocess.Popen([
            "ttyd", "-W", "-p", str(port),
            "-t", "fontSize=18",
            "docker", "exec", "-it",
            "-e", f"STUDENT_NAME={name}",
            "-e", f"BUCKET_NAME={BUCKET_NAME}",
            "-e", f"BOARD_URL=http://{EC2_IP}:5000/board",
            container_name, "python3", "/home/student/quiz.py"
        ])

        sessions[session_id] = {
            "name": name,
            "container": container_name,
            "port": port,
            "start_time": time.time()
        }

        return jsonify({
            "message": "Lab started",
            "session_id": session_id,
            "url": f"http://{EC2_IP}:{port}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Leaderboard from S3
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    s3 = boto3.client("s3")
    results = []

    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        if "Contents" in response:
            for obj in response["Contents"]:
                file = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                data = json.loads(file["Body"].read().decode())
                results.append(data)

        #  Sort leaderboard
        results.sort(key=lambda x: (-x["score"], x["time"]))

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Cleanup (optional manual)
@app.route("/cleanup/<session_id>", methods=["POST"])
def cleanup(session_id):
    session = sessions.get(session_id)

    if not session:
        return jsonify({"error": "Invalid session"}), 404

    container = session["container"]
    port = session["port"]

    try:
        # Stop container
        subprocess.run(["docker", "rm", "-f", container])

        # Kill ttyd port
        subprocess.run(["fuser", "-k", f"{port}/tcp"])

        return jsonify({"message": "Cleaned up"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Optional: Cleanup ALL (useful for reset)
@app.route("/cleanup_all", methods=["POST"])
def cleanup_all():
    try:
        subprocess.run("docker rm -f $(docker ps -aq)", shell=True)
        subprocess.run("pkill ttyd", shell=True)
        return jsonify({"message": "All cleaned"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#  Run app
if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
