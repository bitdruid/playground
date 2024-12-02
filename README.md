![Version](https://img.shields.io/badge/Version-0.1.5-blue.svg)
![Release](https://img.shields.io/badge/Release-Alpha-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Docker Pulls](https://img.shields.io/docker/pulls/bitdruid/osintbot.svg)](https://hub.docker.com/r/bitdruid/osintbot/)

# osintbot
Playing around with possibilities of an osint-bot for discord inside a docker container.

## capabilities

- [x] whois
- [x] arecord
- [x] iplookup
- [x] geoip
- [x] screenshot with printable pdf

## planned

- [ ] portscan

## Installation

Populate .env with the table below or just pull the image from dockerhub (click on the badge above)

```
docker build -t osintbot .
docker run -d --name osintbot osintbot --env-file .env
```
or docker-compose
```
docker-compose up -d
```


### Environmental Variables

<!-- #### general

| env               | description                                          | default       |
|-------------------|------------------------------------------------------|---------------|
| ADMIN_MAIL        | address to receive admin notifications               |               |
| ADMIN_INTERVAL    | interval to send admin notifications                 | 7d            | -->

#### discord bot

If at least the bot token is not given, the bot will not be started.

| env               | description                                          | default       |
|-------------------|------------------------------------------------------|---------------|
| BOT_TOKEN         | API-token of the bot                                 | must be given |
| BOT_NAME          | name of the bot                                      | osintbot      |
| BOT_CHANNEL       | channel the bot will create and post to              | osint         |

#### mail bot

If not given, the mail bot will not be started.

| env               | description                                          | default       |
|-------------------|------------------------------------------------------|---------------|
| MAIL_IMAP_SERVER  | imap server to receive mails                         |               |
| MAIL_IMAP_PORT    | imap port                                            | 993           |
| MAIL_SMTP_SERVER  | smtp server to send mails                            |               |
| MAIL_SMTP_PORT    | smtp port                                            | 587           |
| MAIL_USER         | mail user                                            |               |
| MAIL_PASS         | mail password                                        |               |

#### webui for log and database

| env               | description                                          | default       |
|-------------------|------------------------------------------------------|---------------|
| WEB_LOG           | enable view of log files via webui                   | false         |
| WEB_SQLITE        | enable view of sqlite database via sqlite-web        | false         |

### Volumes

Optional volumes to persist data:

| volume                | description                                          |
|-----------------------|------------------------------------------------------|
| /app/database         | sqlite database                                      |
| /app/documents        | discord documents                                    |
| /app/logs             | log files                                            |

### Ports

You may map the following ports (e.g. `-p 8080:5001`):

| port                  | description                                          |
|-----------------------|------------------------------------------------------|
| 5001                  | log files via webui                                  |
| 5002                  | sqlite database via sqlite-web                       |

## used

### api

- [ipinfo.io](https://ipinfo.io/)
- [iplocation.net](https://iplocation.net/)
- [ipapi.com](https://ip-api.com/)
- [ipapi.co](https://ipapi.co/)
- [freegeoip.live](https://freegeoip.live/)

### repositories

- [whois](https://github.com/rfc1036/whois)
- [sqlite-web](https://github.com/coleifer/sqlite-web)

## Dev & Test

create a virtualenv and install the requirements

```
bash dev/venv_create.sh
```

create file with environment variables in project root

```
touch .env
```

add envs like

```
BOT_TOKEN=<token of your bot>
...
```

build and run docker with

```
bash dev/build_docker.sh
```
