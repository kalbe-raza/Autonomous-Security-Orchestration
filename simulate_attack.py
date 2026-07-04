import requests
import threading
import time

TARGET = "http://localhost:80"

ATTACKS = [
    "/../../etc/passwd",
    "/../../etc/shadow",
    "/?id=1 UNION SELECT username,password FROM users--",
    "/?search=<script>alert('xss')</script>",
    "/admin",
    "/login",
    "/wp-admin",
    "/",
]

def brute_force(n=50):
    print(f"[*] Sending {n} rapid requests to trigger rate limit...")
    for i in range(n):
        try:
            requests.get(TARGET + "/", timeout=2)
        except:
            pass
    print("[*] Brute force done.")

def pattern_attack():
    print("[*] Sending suspicious pattern requests...")
    for path in ATTACKS:
        try:
            r = requests.get(TARGET + path, timeout=2)
            print(f"    {path} → {r.status_code}")
        except Exception as e:
            print(f"    {path} → ERROR: {e}")
        time.sleep(0.3)
    print("[*] Pattern attack done.")

if __name__ == "__main__":
    print("=== Attack Simulator ===")
    print("1. Brute force (rate limit trigger)")
    print("2. Suspicious patterns (SQLi, XSS, path traversal)")
    print("3. Both")
    choice = input("Choose [1/2/3]: ").strip()

    if choice == "1":
        brute_force()
    elif choice == "2":
        pattern_attack()
    elif choice == "3":
        t1 = threading.Thread(target=brute_force)
        t2 = threading.Thread(target=pattern_attack)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    else:
        print("Invalid choice.")
