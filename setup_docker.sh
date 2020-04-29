docker stop who-say-bot
docker rm who-say-bot
docker image rm who-say-bot:latest
docker build . -t who-say-bot
docker run -d --restart always --name who-say-bot who-say-bot
