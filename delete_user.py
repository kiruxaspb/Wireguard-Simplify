import os
import sys

cmdline_arguments = sys.argv

if len(cmdline_arguments) != 2:
    print("Incorrect number of arguments.")
    exit()

name = cmdline_arguments[1]

#get contents of the server config file
file =  open("wg0.conf", "r")
lines = file.readlines()
file.close()

name_string_number = None

#find user info section
for i in range(len(lines)):
    if lines[i].rstrip() == "# " + name:
        name_string_number = i

#exit if not found
if name_string_number == None:
    print("User not found.")
    exit()

config_section_index = name_string_number - 2

#delete user config info (5 lines)
for i in range(5):
    del lines[config_section_index]


#write contents back to the file
with open("wg0.conf", "w") as file:
    for line in lines:
        file.write(line)

file.close()

#delete user config folder
os.system(f"rm -r {name}")

#restart the service
os.system("systemctl restart wg-quick@wg0.service")