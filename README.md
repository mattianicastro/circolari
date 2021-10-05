# Notifier per circolari

Un semplice script che notifica la pubblicazione di una nuova [circolare](https://www.iiscastelli.edu.it/pager.aspx?page=circolari) sul sito dell'IIS Castelli tramite Webhook Discord e Telegram

# Setup

## Clonare il repository 

```bash
git clone https://github.com/mattianicastro/circolari
cd circolari
```

## Installare i requisiti

```bash
pip install -r requirements.txt
```

## Compilare il file di config
```
cp config.example.py config.py
```
Modificare i campi del config

`discord_webhook` = url del [webhook di Discord](https://support.discord.com/hc/it/articles/228383668-Come-usare-i-Webhooks)

`telegram_token` = https://core.telegram.org/bots#6-botfather

`telegram_chat_id` = id della chat Telegram dove verranno inviate le notifiche
- Per ottenere l'id sarà necessario aggiungere il bot nella chat ed eseguire `
curl https://api.telegram.org/bot$BOT_TOKEN/getUpdates
`

## Prima esecuzione

Al fine di evitare l'inoltro delle circolari pregresse sarà necessario **solo per la prima volta** eseguire
```bash
python main.py cache
```

## Crontab

Lo script è progettato per essere eseguito **ogni ora** (tempo raccomandato) in modo da poter accertare la presenza di nuove circolari. A tal fine è consigliato utilizzare `crontab` in questo modo

```bash
crontab -e

0 * * * * /path/to/python3 /path/to/main.py
```
