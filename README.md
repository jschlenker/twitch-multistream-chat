# Twitch multi stream bot
Run a bot which joins the chat of multiple Twitch streams.

## Requirements

You only need python (>= 3.6)! :smile:

## Set up

### Downloading the files

Clone or download this repository.

```bash
git clone https://github.com/jschlenker/twitch-multistream-chat.git
```

### Editing the config file

The `config.json` file has a few parameters you have to set:
- `bot_username` is the username of the bot. Replace `<USERNAME>`.
- `oauth_token` is the oauth token for the bot user you can generate [here](https://twitchapps.com/tmi/).
- `channels` is a list of the channels which are involved in your multi stream. Just replace `<CHANNEL1>` and `<CHANNEL2>` and add more of needed.
- `whitelist` is a whitelist with users that should be able to send across the channels. Leave empty if not needed.
- `blacklist` is a blacklist with the users that should not be able to send across the channels, i.e., bots or users with chat ban in one of the participating channels.

## Run the bot

On windows you should be able to just double click the `bot.py`  file after setting up the `config.json` file.

You can also just run
```bash
python bot.py
```
or
```bash
python3 bot.py
```
if `python` defaults to Python2.7.

If you have multiple configs for different occasions, you can also specify the location of a config file by passing it with the `-c`/`--config` flag:

```bash
python bot.py -c PATH/TO/MY/CONFIG.json
```

