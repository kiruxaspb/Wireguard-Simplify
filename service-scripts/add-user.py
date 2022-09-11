import os
import sys
import urllib.request


PORT = "51820"
PATH = os.path.abspath(os.getcwd())
PEER_PATH = os.path.abspath(os.getcwd()) + "/peers"
SERVER_GLOBAL_IP = urllib.request.urlopen('https://ident.me').read().decode('utf8')


def get_available_ip() -> str:
    taken_ips = []
    subnet_ips = []

    with open("wg0.conf", "r") as file:
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

    print("All addresses are taken.")
    exit()


def get_user_list() -> list:
    users = []

    with open("wg0.conf", "r") as file:
        for line in file:
            if line.startswith("#"):
                users.append((line.rstrip()).split()[1])
    
    return users


cmdline_arguments = sys.argv

if len(cmdline_arguments) != 2:
    print("Incorrect number of arguments.")
    exit()

name = cmdline_arguments[1]

if name in get_user_list():
    print("User already exists.")
    exit()
    

ip = get_available_ip()

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
file = open(f"{PATH}/server/publickey", "r")
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
file = open(f"wg0.conf", "a")
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

#restart the service
os.system(f"systemctl restart wg-quick@wg0.service")
