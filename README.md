# KrakenDCAPy

Simple command-line tool for automated dollar-cost averaging (DCA) of Bitcoin purchases on the Kraken exchange with limit orders on the BTC-EUR pair.

## Requirements

 - requests
 - python-dotenv
 - urllib3
 - certifi
 - charset-normalizer
 - idna

Install the required packages with `pip install -r requirements.txt`.

Optional : Mailgun account to send email notifications.

Tested with Python 3.10.12

## Setup

Create an API key on Kraken with "Query" and "Create & modify orders" permissions.

Create a `.env` file containing :
 - API_KEY : Kraken API key
 - SECRET : Kraken API key's secret
 - EMAIL_USER (optional) : Mailgun username
 - EMAIL_PASSWORD (optional) : Mailgun password

## Usage

`python main.py --amount 20 --spread 10 --funds-limit 50 --email email@example.com`

 - `--amount 20` : Place a limit order for 20 EUR
 - `--spread 10` : Set the limit order at 10 EUR less than the current bid price
 - `--funds-limit 50` : If balance is less than 50 EUR, send an email notification and don't place the order
 - `--email email@example.com` : Email address that will receive the notification