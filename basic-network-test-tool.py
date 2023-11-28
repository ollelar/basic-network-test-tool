import socket
import subprocess
import requests
import platform
import re
import threading
import sys
import time


# Spinning cursor
def spinning_cursor():
    while True:
        for cursor in "|/-\\":
            yield cursor


spinner = spinning_cursor()


def spinning():
    while True:
        sys.stdout.write(next(spinner))  # write the next character
        sys.stdout.flush()  # flush stdout buffer (actual character display)
        sys.stdout.write("\b")  # erase the last written char
        time.sleep(0.1)


# Start spinning in a separate thread
def start_spinner():
    t = threading.Thread(target=spinning)
    t.daemon = True  # Daemon thread ends when main thread ends
    t.start()


def ping(host, count=4, timeout=2):
    """
    Returns the average latency and packet loss to a host using ping
    """
    start_spinner()

    # Ping parameters as function of OS
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"

    # Building the command
    command = ["ping", param, str(count), timeout_param, str(timeout), host]

    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, universal_newlines=True
        )

        # Parse packet loss
        packet_loss = re.search(r"(\d+)% packet loss", output)
        packet_loss = packet_loss.group(1) if packet_loss else "100"

        # Parse latency
        latency = re.search(r"Average = (\d+ms)|time=(\d+.\d+) ms", output)
        latency = latency.group(1) or latency.group(2) if latency else "N/A"

        return latency, packet_loss
    except subprocess.CalledProcessError as e:
        print(f"\033[91m✗\033[0m Ping: {e.output}")
        return "N/A", "100%"
    finally:
        sys.stdout.write("\b \b")  # Erase spinner


def check_dns(host="www.google.com"):
    """
    Tries to resolve DNS and returns True if successful
    """
    start_spinner()

    try:
        socket.gethostbyname(host)
        return True
    except socket.error as e:
        print(f"\033[91m✗\033[0m DNS Resolution: {e}")
        return False
    finally:
        sys.stdout.write("\b \b")  # Erase spinner


def check_http_request(url="http://www.httpbin.org"):
    """
    Tries to perform an HTTP request and returns True if successful
    """
    start_spinner()

    try:
        response = requests.get(url)
        return True if response.status_code == 200 else False
    except requests.RequestException as e:
        print(f"\033[91m✗\033[0m HTTP Request: {e}")
        return False
    finally:
        sys.stdout.write("\b \b")  # Erase spinner


# Test Ping (Latency and Packet Loss)
latency, packet_loss = ping("www.google.com")
print(
    f"\033[92m✓\033[0m Ping. Latency: {latency}, Packet Loss: {packet_loss}"
    if packet_loss != "100%"
    else "\033[91m✗\033[0m Packet Loss"
)

# Test DNS resolution
dns_status = check_dns()
print(f"\033[92m✓\033[0m DNS Resolution" if dns_status else "")

# Test HTTP request (Internet Access)
http_status = check_http_request()
print(f"\033[92m✓\033[0m Internet Access" if http_status else "")
