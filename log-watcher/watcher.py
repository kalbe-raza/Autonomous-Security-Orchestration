import time
import re
import requests
import os
from collections import defaultdict

LOG_FILE = "/logs/access.log"
N8N_WEBHOOK_URL = os.environ["N8N_WEBHOOK_URL"]

THRESHOLD = 20        # requests from one IP within the window
WINDOW_SECONDS = 10   # time window in seconds

SUSPICIOUS_PATTERNS = [
    r"(\.\.\/|\.\.\\)",          # path traversal
    r"(union.*select|select.*from|drop\s+table)",  # SQL injection
    r"(<script|javascript:)",    # XSS
    r"(/etc/passwd|/etc/shadow)", # file inclusion
    r"(\?.*=.*http[s]?://)",     # open redirect
]

ip_requests = defaultdict(list)


def is_suspicious_request(request_line):
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, request_line, re.IGNORECASE):
            return True
    return False


def check_rate(ip):
    now = time.time()
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < WINDOW_SECONDS]
    ip_requests[ip].append(now)
    return len(ip_requests[ip]) >= THRESHOLD


def send_alert(ip, log_lines, reason):
    payload = {
        "attacker_ip": ip,
        "reason": reason,
        "log_sample": log_lines[-5:],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        print(f"[ALERT SENT] IP: {ip} | Reason: {reason}")
    except Exception as e:
        print(f"[ERROR] Failed to send alert: {e}")


def tail_log(filepath):
    with open(filepath, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line


def main():
    print(f"[*] Watching {LOG_FILE} for attacks...")
    alerted_ips = set()

    for line in tail_log(LOG_FILE):
        parts = line.split()
        if not parts:
            continue

        ip = parts[0]

        if ip in alerted_ips:
            continue

        if is_suspicious_request(line):
            alerted_ips.add(ip)
            send_alert(ip, [line], "Suspicious pattern detected")
            continue

        if check_rate(ip):
            alerted_ips.add(ip)
            send_alert(ip, [line], f"Rate limit exceeded: {THRESHOLD} requests in {WINDOW_SECONDS}s")


if __name__ == "__main__":
    main()
