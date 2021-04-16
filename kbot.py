#!/usr/bin/env python3

import os
import threading
import asyncio
import random
import sys
import discord
import time


client = discord.Client()
lock = threading.Lock()
BOT_CHANNEL_ID = ''
ID_DELAY=12
DB_DELAY=6
PATH="/home/conor/KelseyBot/Discord_Bot/"
PARITY_CHECK = 1


#K,V dictionary setup as {Author: {Title : Link ? ""}}
books = {}

def get_token():
    with open(PATH + "token", 'r') as fil:
        lines = fil.readline().rstrip()
        fil.close()
        return lines

tok = "ODI2NTY1ODk4MzExNDM0Mjkw.YGOVew.Ge98O0jCbwuulB3a3fz81_fiUh0"


#Asynchronously deletes messages
async def delete_msg(msg):
    try:
        await msg.delete()
    except:
        pass


#Commands List
def build_cmds():
    msg = "**Hello! This is a list of commands and tags I can use!**\n"
    msg += "**!cmds** - Lists all commands available to the bot\n\n"
    msg += "**!add** - This function will add a book to the list of books\n"
    msg += "\t **-t** indicates the book title given as -t book_title\n"
    msg += "\t **-a** indicates the book author given as -a author\n"
    msg += "\t **-l** indicates a link where one may read or purchase the book (this command is optional)\n"
    msg += "\n"
    msg += "**!delete** - This function will delete either a single entry, or all books by an author\n"
    msg += "\t **-a** The author tag is necessary so deleting books with same titles don\'t cause issues\n"
    msg += "\t **-t** The title tag indicates the book title\n"
    msg += "\n"
    msg += "**!search** - This function will either return a list of books by a certain author, or can return a single book and its associated information. Use either the -a or -t tag (but not both)\n"
    msg += "\n"
    msg += "**!display_all** - This function will display all books in the list by author (warning, if there are many books in the list the message will be long)\n"
    return msg


def search_by_author(author):
    msg = "Books by **{}**:\n".format(author)
    if author in books:
        for book in books[author]:
            if book == '':
                msg += "\n__{}__\n".format(book)
            else:
                msg += "\t__{}__\n\t{}\n".format(book, books[author][book])
        return msg
    else:
        return "No authors by that name found"


def search_by_title(title):
    for author in books:
        for book in books[author]:
            if book == title:
                if books[author][book] != '':
                    return "{} By {}\nCan be found at: {}".format(book, author, books[author][book])
                else:
                    return "{} By {}\n".format(book, author)
    return "Book could not be found"
            

def display_all():
    msg = ''
    auths = sorted(books.keys())
    for auth in auths:
        msg += search_by_author(auth)
    return msg




def delete_by_author(author):
    lock.acquire()
    global PARITY_CHECK
    ret = books.pop(author,None)
    if ret is not None:
        PARITY_CHECK += 1
    lock.release()
    return ret

def delete_by_title(title):
    lock.acquire()
    global PARITY_CHECK
    for author in books:
        for book in books[author]:
            if book == title:
                books[author].pop(title, None)
                PARITY_CHECK += 1
                lock.release()
                return 1
    lock.release()
    return None

#message structure will use a tagging system
def add_book(info):
    global PARITY_CHECK

    lock.acquire()
    global PARITY_CHECK
    if info[0] in books:
        book = books[info[0]]
        if info[1] in book and len(info) == 3 and book[info[1]] == info[2]:
            lock.release()
            return 0
        
        elif info[1] in book and len(info) == 3 and book[info[1]] != info[2]:
            books[info[0]][info[1]] = info[2]
            PARITY_CHECK += 1
            lock.release()
            return 1
        else:
            if len(info) == 2:
                books[info[0]][info[1]] = ''
            else:
                books[info[0]][info[1]] = info[2]
    else:
        if len(info) == 2:
            books[info[0]] = {info[1] : ''}
        else:
            books[info[0]] = {info[1] : info[2]}
    PARITY_CHECK += 1
    lock.release()
    return 2



def backup_book_thread():
    global PARITY_CHECK

    while True:
        time.sleep(3600 * DB_DELAY)
        if not os.path.exists(PATH + "Books"):
            lock.acquire()
            f = open(PATH + "Books", "w")
            f.write("1\n")
            for author in books:
                for book in books[author]:
                    f.write("{},{},{}\n".format(author, book, books[author][book]))
            f.close()
            lock.release()
        else:
            f = open(PATH + "Books", 'r')
            parity = f.readline()
            if int(parity) != PARITY_CHECK:
                f.close()
                lock.acquire()
                os.remove(PATH + "Books")
                f = open(PATH + "Books", 'w')
                f.write("{}\n".format(PARITY_CHECK))
                for author in books:
                    for book in books[author]:
                        f.write("{},{},{}\n".format(author, book, books[author][book]))
                f.close()
                lock.release()
            else:
                f.close()

def backup_id_thread():
    global BOT_CHANNEL_ID
    
    while True:
        time.sleep(3600 * ID_DELAY)
        if not os.path.exists(PATH + "CID"):
            os.system("touch {}CID".format(PATH))
        with open(PATH + "CID", 'w') as f:
            lock.acquire()
            f.write(str(BOT_CHANNEL_ID))
        f.close()
        lock.release()

def shutdown_restore():
    global BOT_CHANNEL_ID
    global PARITY_CHECK

    if os.path.exists(PATH + "CID"):
        lock.acquire()
        f = open(PATH + "CID", 'r')
        BOT_CHANNEL_ID = int(f.readline().rstrip()) 
        lock.release()

    if os.path.exists(PATH + "Books"):
        f = open(PATH + "Books", 'r')
        PARITY_CHECK = int(f.readline().rstrip())
        line = f.readline().rstrip()
        while line:
            add_book(line.split(","))
            line = f.readline().rstrip()
        f.close()







@client.event
async def on_ready():
    print(str(client.user) + " has connected to Discord!")
    shutdown_restore()
    id_thread = threading.Thread(target = backup_id_thread)
    book_thread = threading.Thread(target = backup_book_thread)
    id_thread.start()
    book_thread.start()
    print("Threads Have Begun...")
    while True:
        if BOT_CHANNEL_ID == '':
            await client.change_presence(activity=discord.Game(name="Please run !fts #Channel"))
        else:
            await client.change_presence(activity=discord.Game(name="Stardew Valley"))

        await asyncio.sleep(360)

@client.event
async def on_message(message):
    global BOT_CHANNEL_ID
    if message.author == client.user:
        return
    elif message.content.startswith("!cmds"):
        await message.delete()
        channel = client.get_channel(BOT_CHANNEL_ID)
        cmds = await channel.send(build_cmds())
        pins = await channel.pins()
        for pin in pins:
            if pin.author == client.user:
                await pin.delete()
        await cmds.pin()
        
    elif message.content.startswith("!delete"):
        if "-a" in message.content:
            ret = delete_by_author(message.content[11:].lower().title().strip())
        else:
            ret = delete_by_title(message.content[11:].lower().title().strip())
        if ret is not None:
            bot_msg = await message.channel.send("Title or Author Successfully Deleted!")
            lock.acquire()
            lock.release()
        else:
            bot_msg = await message.channel.send("No deletion occured, either due to error or missing search object")
        await asyncio.sleep(60)
        await delete_msg(bot_msg)
        await delete_msg(message)

    elif message.content.startswith("!add"):
        add = ["", "", ""]
        info = message.content[6:].split("-")
        for block in info:
            print("Block: ", block)
            if block[0] == 'a':
                add[0] = block[2:].lower().title().strip()
            elif block[0] == 't':
                add[1] = block[2:].lower().title().strip()
            elif block[0] == 'l':
                add[2] = block[2:].strip()
        res = add_book(add)
        if res == 2:
            bot_msg = await message.channel.send("Book has been successfully added!")
        elif res == 0:
            bot_msg = await message.channel.send("Looks like that book's been added before")
        else:
            bot_msg = await message.channel.send("Entry has been updated")
        await asyncio.sleep(30)
        await delete_msg(bot_msg)
        await delete_msg(message)

    elif message.content.startswith("!fts"):
        if BOT_CHANNEL_ID != '':
            bot_msg = await message.channel.send("You've already completed first time setup, if you want to change the bot\'s channel please use the !change_channel command")
            await asyncio.sleep(60)
            await delete_msg(bot_msg)
            await delete_msg(message)
        else:
            BOT_CHANNEL_ID = int(message.content.split(" ")[1][2:-1])
            bot_msg = await message.channel.send("I should be all good to go, thanks!")
            await asyncio.sleep(30)
            await delete_msg(bot_msg)
            await delete_msg(message)
    
    elif message.content.startswith("!search"):
        if "-a" in message.content:
            bot_msg = await message.channel.send(search_by_author(message.content[11:].lower().title()))
            await asyncio.sleep(360)
            await delete_msg(bot_msg)
            await delete_msg(message)
        else:
            bot_msg = await message.channel.send(search_by_title(message.content[11:].lower().title()))
            await asyncio.sleep(360)
            await delete_msg(bot_msg)
            await delete_msg(message)

    elif message.content.startswith("!display_all"):
        bot_msg = await client.get_channel(BOT_CHANNEL_ID).send(display_all())
        await asyncio.sleep(720)
        await delete_msg(bot_msg)
        await delete_msg(message)

    else:
        print("Invalid Message")


try:
    client.run(tok)
except TypeError:
    os.system("python3 -m pip install -U discord.py")
    try:
        client.run(tok)
    except:
        print("Somethings gone wrong")

