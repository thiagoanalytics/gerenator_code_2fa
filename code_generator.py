# arquivo: totp_runner.py
import os, time
import pyotp
from dotenv import load_dotenv

load_dotenv()  # carrega .env se existir

secret = os.getenv("TOTP_SECRET")
if not secret:
    raise SystemExit("TOTP_SECRET necessária no .env ou variável de ambiente.")

totp = pyotp.TOTP(secret)
code = totp.now()
interval = totp.interval
remaining = interval - (int(time.time()) % interval)

print(f"Código: {code}  (expira em {remaining}s)")
