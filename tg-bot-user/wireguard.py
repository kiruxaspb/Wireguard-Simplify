import sys
import os
import urllib.request
import time
from dataclasses import dataclass


PEER_PATH = "/etc/wireguard/peers"
SERVER_PATH = "/etc/wireguard/server"
WG_CONFIG_PATH = "/etc/wireguard/wg0.conf"
WG_INFO_PATH = "/etc/wireguard/info.txt"
SERVER_GLOBAL_IP = urllib.request.urlopen('https://ident.me').read().decode('utf8')
PORT = "51820"


@dataclass
class Peer:
    allowed_ip: str
    public_key: str

        
def get_available_ip() -> str or None:
    taken_ips = []
    subnet_ips = []

    with open(WG_CONFIG_PATH, "r") as file:
        for line in file:
            if line.startswith("AllowedIPs"):
                taken_ips.append(line.rstrip())

    for i in range(len(taken_ips)):
        taken_ips[i] = (taken_ips[i].split("="))[1].lstrip()


    for i in range(2, 254):
        subnet_ips.append(f"10.13.13.{i}/32")

    for ip in subnet_ips:
        if ip not in taken_ips:
            return ip

    
def create_peer(name) -> Peer or None:
    ip = get_available_ip()
    
    if ip is None:
        return 

    # create peer directory
    os.system(f"mkdir {PEER_PATH}/{name}")

    # generate files with private and public keys
    os.system(f"wg genkey | tee {PEER_PATH}/{name}/{name}_privatekey | wg pubkey | tee {PEER_PATH}/{name}/{name}_publickey")

    # get keys from generated files
    file = open(f"{PEER_PATH}/{name}/{name}_privatekey", "r")
    private_key = (file.readline()).rstrip()
    file.close()

    file = open(f"{PEER_PATH}/{name}/{name}_publickey", "r")
    public_key = (file.readline()).rstrip()
    file.close()

    # get server public key
    file = open(f"{SERVER_PATH}/publickey", "r")
    server_public_key = (file.readline()).rstrip()
    file.close()

    #write to client config file
    file = open(f"{PEER_PATH}/{name}/{name}.conf", "w")
    file.write(f"[Interface]\n")
    file.write(f"Address = {ip[:-3]}\n")
    file.write(f"PrivateKey = {private_key}\n")
    file.write(f"ListenPort = {PORT}\n")
    file.write(f"DNS = 8.8.8.8\n")
    file.write(f"\n")
    file.write(f"[Peer]\n")
    file.write(f"PublicKey = {server_public_key}\n")
    file.write(f"Endpoint = {SERVER_GLOBAL_IP}:{PORT}\n")
    file.write(f"AllowedIPs = 0.0.0.0/0\n")
    file.close()

    #write to server config file
    file = open(WG_CONFIG_PATH, "a")
    file.write("\n")
    file.write(f"[Peer]\n")
    file.write(f"# {name}\n")
    file.write(f"PublicKey = {public_key}\n")
    file.write(f"AllowedIPs = {ip}\n")
    file.close()

    #generate qr
    os.system(f"qrencode -t png -o {PEER_PATH}/{name}/qr.png < {PEER_PATH}/{name}/{name}.conf")

    file = open(f"{PEER_PATH}/{name}/qr.sh", "w")
    file.write(f"#!/bin/bash\n")
    file.write(f"qrencode -t utf8 <  {PEER_PATH}/{name}/{name}.conf")
    file.close()

    os.system(f"chmod ugo+x {PEER_PATH}/{name}/qr.sh")

    return Peer(ip, public_key)


def restart_wireguard() -> None:
    os.system(f"systemctl restart wg-quick@wg0.service")


def count_connected():
    #update information dump file
    os.system(f"wg show wg0 dump > {WG_INFO_PATH}") 

    last_handshakes = []

    with open(WG_INFO_PATH, "r") as file:
        for i, line in enumerate(file):
            if i != 0: #ignores wg config line
                line = line.split()
                last_handshakes.append(line[4])

    connected_count = 0
    for handshake in last_handshakes:
        if int(handshake) > time.time() - 120:
            connected_count += 1

    return connected_count



    

