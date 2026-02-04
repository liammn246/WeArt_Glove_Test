"""Simple UDP receiver for testing closure packets from the middleware script.

Expects packets in format: [seq:uint8][thumb:uint8][index:uint8][middle:uint8][ring:uint8][pinky:uint8]
Listens on 127.0.0.1:5005 by default (change UDP_IP/UDP_PORT if needed).
Run alongside `closure.py` to verify packets being sent.
"""
import socket
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

def byte_to_norm(b):
    return b / 255.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"UDP receiver listening on {UDP_IP}:{UDP_PORT}")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        ts = time.time()
        if len(data) < 6:
            print(f"[{ts:.3f}] Received short packet ({len(data)} bytes) from {addr}")
            continue
        try:
            seq, t, i, m, r, p = struct.unpack('!6B', data[:6])
        except struct.error:
            print(f"[{ts:.3f}] Failed to unpack packet from {addr}, raw len={len(data)}")
            continue
        print(f"[{ts:.3f}] seq={seq}  T={t} I={i} M={m} R={r} P={p}  (norm: T={byte_to_norm(t):.3f} I={byte_to_norm(i):.3f} M={byte_to_norm(m):.3f} R={byte_to_norm(r):.3f} P={byte_to_norm(p):.3f})")
except KeyboardInterrupt:
    print("\nReceiver stopped by user")
finally:
    sock.close()
