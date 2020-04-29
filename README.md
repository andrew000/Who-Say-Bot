# Who_Say_Bot

A [Telegram](https://telegram.org) Bot for Base64 Encoding/Decoding

### Inline is available!

# Requirements:
* Telegram token (use [@BotFather](https://t.me/botfather) to get one)
* Linux: <code>pip3 install -r requirements.txt</code>
* Windows: <code>pip install -r requirements.txt</code>

# Config:
1. Turn On "Inline Mode" in [@BotFather](https://t.me/botfather)
2. Paste your token in config.py
3. Run <code>python3 main.py</code>

# Docker:
```
docker build . -t who-say-bot
docker run -d --restart who-say-bot
```