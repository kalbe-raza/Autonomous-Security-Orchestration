import subprocess
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

blocked_ips = set()


def is_valid_ip(ip):
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) is not None


@app.route("/block", methods=["POST"])
def block_ip():
    data = request.get_json()
    ip = data.get("ip", "").strip()

    if not is_valid_ip(ip):
        return jsonify({"error": "Invalid IP address"}), 400

    if ip in blocked_ips:
        return jsonify({"status": "already_blocked", "ip": ip}), 200

    try:
        subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=True, capture_output=True
        )
        blocked_ips.add(ip)
        print(f"[BLOCKED] {ip}")
        return jsonify({"status": "blocked", "ip": ip}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr.decode()}), 500


@app.route("/blocked", methods=["GET"])
def list_blocked():
    return jsonify({"blocked_ips": list(blocked_ips)}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
