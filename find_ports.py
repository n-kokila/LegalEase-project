import socket
import random
import sys
from pathlib import Path

def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a specific TCP port is free for binding on host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
        except OSError:
            return False

def get_random_free_port(min_port: int, max_port: int, host: str = "127.0.0.1") -> int:
    """Find a random available port in [min_port, max_port]."""
    ports = list(range(min_port, max_port + 1))
    random.shuffle(ports)
    for port in ports:
        if is_port_free(port, host):
            return port
    # Fallback to OS assigned ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]

def save_port_to_file(filename: str, port: int):
    """Save the allocated port to a local file for cross-process discovery."""
    try:
        current_dir = Path(__file__).resolve().parent
        file_path = current_dir / filename
        file_path.write_text(str(port), encoding="utf-8")
    except Exception:
        pass

def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "both"

    if mode == "backend":
        bp = get_random_free_port(8001, 8499)
        save_port_to_file(".backend_port", bp)
        print(bp)
    elif mode == "frontend":
        fp = get_random_free_port(8502, 8999)
        save_port_to_file(".frontend_port", fp)
        print(fp)
    else:  # "both"
        bp = get_random_free_port(8001, 8499)
        save_port_to_file(".backend_port", bp)

        fp = get_random_free_port(8502, 8999)
        while fp == bp:
            fp = get_random_free_port(8502, 8999)
        save_port_to_file(".frontend_port", fp)

        # Print both separated by space for batch token parsing
        print(f"{bp} {fp}")

if __name__ == "__main__":
    main()
