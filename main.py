import requests, os, hashlib, base64, hmac, urllib, argparse
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--amount', type=int, default=10)
parser.add_argument('--spread', type=int, default=10)
parser.add_argument('--funds-limit', type=int, default=50)
parser.add_argument('--email', type=str)
args = parser.parse_args()

params = {**vars(args)}

if os.getenv("API_KEY") is None or os.getenv("SECRET") is None:
    print("Create an API key on Kraken and write API_KEY and SECRET to .env")
    exit(1)

if params["email"] is not None and os.getenv("EMAIL_USER") is not None and os.getenv("EMAIL_PASSWORD") is not None:
    params["email_enabled"] = True
else:
    params["email_enabled"] = False

def main():
    balance = get_balance("ZEUR")

    if balance < params['funds_limit']:
        msg = f"Account balance is {balance} EUR which is below the configured threshold ({params['funds_limit']} EUR). Please add more funds."
        print(f"{print_date()} {msg}")

        if params["email_enabled"] == True:
            import smtplib, ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = "smtp.mailgun.org"
            port = 465
            sender_email = os.getenv("EMAIL_USER")
            password = os.getenv("EMAIL_PASSWORD")

            message = MIMEMultipart("alternative")
            message["Subject"] = "[Kraken DCA] Insufficient funds"
            message["From"] = sender_email
            message["To"] = params['email']

            text = f"Account balance is {balance} EUR which is below the configured threshold ({params['funds_limit']} EUR). Please add more funds."
            part = MIMEText(text, "plain")
            message.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, params['email'], message.as_string())

            print(f"{print_date()} Email sent to {params['email']}")
        
        exit(1)

    if balance >= params['amount']:
        res = kraken("Ticker", { 'pair': 'BTCEUR' })
        set_bid_price = float(res['result']['XXBTZEUR']['b'][0]) - params['spread']

        res = kraken("AddOrder", {
            'ordertype': "limit",
            'type': "buy",
            'volume': params['amount'] / set_bid_price,
            'pair': 'XXBTZEUR',
            'price': set_bid_price,
            'oflags': 'post',
            'validate': False
        }, True)

        if len(res['error']) == 0:
            print(f"{print_date()} {res['result']['descr']['order']}")
            exit(0)
        else:
            print(f"{print_date()} {res['error'][0]}")
            exit(1)
    else:
        print(f"{print_date()} Insufficient balance")
        exit(1)

def get_balance(account):
    res = kraken("Balance", {}, True)
    return float(res['result'][account])

def kraken(method, request, privateMethod = False):
    if privateMethod:
        uri = '/0/private/' + method
    else:
        uri = '/0/public/' + method

    url = "https://api.kraken.com" + uri
    api_key = os.getenv("API_KEY")
    secret = os.getenv("SECRET")

    request['nonce'] = int(datetime.now().timestamp() * 1000)

    postdata = urllib.parse.urlencode(request)
    encoded = (str(request['nonce']) + postdata).encode()
    message = uri.encode() + hashlib.sha256(encoded).digest()
    signature = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(signature.digest())
    api_sign = sigdigest.decode()

    headers = {
        'API-Key': api_key,
        'API-Sign': api_sign,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    data = urllib.parse.urlencode(request)
    res = requests.post(url, data=data, headers=headers)

    return res.json()

def print_date():
    return datetime.now().strftime("[%d/%m/%Y %H:%M]")

if __name__ == "__main__":
    main()