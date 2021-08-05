import json
import random
import socket
import ssl
import threading
import time
from typing import Tuple
from argparse import ArgumentParser

CHANNELS = list()
WHITELIST = list()
BLACKLIST = list()

arg_parser = ArgumentParser()

arg_parser.add_argument("-c", "--config", default="config.json")

def send(irc: ssl.SSLSocket, message: str):
    """Send a message to the given socket.

    Args:
        irc (ssl.SSLSocket): irc socket
        message (str): message to send
    """
    irc.send(bytes(f'{message}\r\n', 'UTF-8'))


def send_pong(irc: ssl.SSLSocket):
    """Send a ping reply message to the given socket

    Args:
        irc (ssl.SSLSocket): irl socket
    """
    send(irc, 'PONG :tmi.twitch.tv')


def serve_channels(irc: ssl.SSLSocket, origin: Tuple[str, str], message: str, channels: list):
    """Serve the message from a given origin to the given channels.

    Args:
        irc (ssl.SSLSocket): irc socket
        origin (Tuple[str, str]): (user, source_channel)
        message (str): message tha should be served
        channels (list): A list of all channels to serve
    """
    user, src_ch = origin

    print("Message from {} in {}".format(*origin))

    for ch in channels:
        if src_ch == ch:
            continue
        # print(f"Sende {message} nach {ch}")
        send_chat(irc, f"{user}: {message}", ch)


def send_chat(irc: ssl.SSLSocket, message: str, channel: str):
    """Send a message to a given channel

    Args:
        irc (ssl.SSLSocket): irc socket
        message (str): message to send
        channel (str): channel to send to
    """
    send(irc, f'PRIVMSG #{channel} :{message}')


def parse_chat(irc: ssl.SSLSocket, raw_message: str):
    """Parses a chat message and calls according action

    Args:
        irc (ssl.SSLSocket): socket
        raw_message (str): message
    """
    components = raw_message.split()
    user, _ = components[0].split('!')[1].split('@')
    channel = components[2]
    message = ' '.join(components[3:])[1:]

    if WHITELIST and (user not in WHITELIST):
        return

    if BLACKLIST and (user in BLACKLIST):
        return

    if message.startswith('!'):
        message_components = message.split()
        command = message_components[0][1:]

        if command == 'dice':
            random_number = random.randint(1, 6)
            send_chat(irc, f'Hi {user}, deine Zahl: {random_number}', channel[1:])
    else:
        origin = (user, channel[1:])
        serve_channels(irc, origin, message, CHANNELS)

def main_loop(irc: ssl.SSLSocket):
    """Main loop running in a thread

    Args:
        irc (ssl.SSLSocket): socket
    """
    while True:
        data_ch = irc.recv(1024)
        raw_message = data_ch.decode('UTF-8')

        for line in raw_message.splitlines():
            if line.startswith('PING :tmi.twitch.tv'):
                send_pong(irc)
            else:
                components = line.split()
                command = components[1]

                if command == 'PRIVMSG':
                    parse_chat(irc, line)
                elif command == 'NOTICE':
                    print("NOTICE: {}".format(line[line.find(":", 1, -1):]))

if __name__ == '__main__':
    args = arg_parser.parse_args()
    with open(args.config, "r") as f:
        config = json.load(f)

    try:
        bot_username = config['bot_username']
        oauth_token = config['oauth_token']
        channels = config['channels']
    except KeyError as e:
        print(f"The config options {e.args[0]} has to be set.")

    CHANNELS = channels
    WHITELIST = config.get("whitelist", list())
    BLACKLIST = config.get("blacklist", list())

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    irc = context.wrap_socket(socket)

    irc.connect(('irc.chat.twitch.tv', 6697))

    send(irc, f'PASS {oauth_token}')
    send(irc, f'NICK {bot_username}')
    for ch in channels:
        send(irc, f'JOIN #{ch}')

    bot_thread = threading.Thread(target=main_loop, args=(irc,), name="bot_loop", daemon=True)
    bot_thread.start()

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        socket.close()
        exit(0)