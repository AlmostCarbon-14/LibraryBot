#!/usr/bin/env python3
import os
import subprocess as sp
import time
import sys

if os.geteuid() != 0:
    sys.exit("Please make sure this program is run as a superuser!")

flag = False
try:
    import discord
except:
    try:
        sp.call(['pip3', 'install', '-U', 'discord.py'])
    except:
        flag = True
        print("There's been an issue installing discord via Pip3, it's possible that pip3 is not installed so we will try doing that first!")
        time.sleep(5)
        os.system("sudo apt-get update -y")
        print("\n{}Update Complete Beginning Upgrade{}".format('*' * 40, '*' * 40))
        time.sleep(5)
        os.system("Sudo apt-get upgrade -y")
        print("\n{}Upgrade Complete Attempting to install pip3{}".format('*' * 40, '*' * 40))
        time.sleep(5)
        os.system("sudo apt-get -y install python3-pip")

if flag:
    print("Attempting to install discord.py again!")
    if sp.call(['pip3', 'install', '-U', 'discord.py']) == 1:
        print("Another error has occured, we're gonna try a different method real quick!")
        time.sleep(5)
        if sp.call(['python3', '-m',  'pip', 'install', '-U', 'discord.py']) == 1:
            sys.exit("Sorry somethings really wrong, please try and do this manually")



print("Everythings setup now, happy botting!")
f = open("/home/pi/Discord_Bot/status.sys", "w")
f.write("")
f.close()

