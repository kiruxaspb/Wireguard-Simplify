import sys
import os
import random


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

    print("All addresses are taken")
    exit()


try:
    name = sys.argv[1]
except IndexError:
    print("Pass peer name as a command line argument!")
    exit()


ip = get_available_ip()


# create peer directory
os.system(f"mkdir {name}")


# generate files with private and public keys
os.system(f"wg genkey | tee /etc/wireguard/{name}/{name}_privatekey | wg pubkey | tee /etc/wireguard/{name}/{name}_publickey")


# get keys from generated files
file = open(f"/etc/wireguard/{name}/{name}_privatekey", "r")
private_key = (file.readline()).rstrip()
file.close()

file = open(f"/etc/wireguard/{name}/{name}_publickey", "r")
public_key = (file.readline()).rstrip()
file.close()


# get server public key
file = open(f"/etc/wireguard/server/publickey", "r")
server_public_key = (file.readline()).rstrip()
file.close()


#write to client config file
file = open(f"/etc/wireguard/{name}/{name}.conf", "w")
file.write(f"[Interface]\n")
file.write(f"Address = {ip[:-3]}\n")
file.write(f"PrivateKey = {private_key}\n")
file.write(f"ListenPort = 51820\n")
file.write(f"DNS = 8.8.8.8\n")
file.write(f"\n")
file.write(f"[Peer]\n")
file.write(f"PublicKey = {server_public_key}\n")
file.write(f"Endpoint = 194.135.20.93:51820\n")
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
os.system(f"qrencode -t png -o /etc/wireguard/{name}/qr.png < /etc/wireguard/{name}/{name}.conf")

file = open(f"/etc/wireguard/{name}/qr.sh", "w")
file.write(f"#!/bin/bash\n")
file.write(f"qrencode -t utf8 < /etc/wireguard/{name}/{name}.conf")
file.close()

os.system(f"chmod ugo+x /etc/wireguard/{name}/qr.sh")


#restart the service
os.system(f"systemctl restart wg-quick@wg0.service")
