import sys
from PIL import Image
from pyzbar.pyzbar import decode
import re

img_path = sys.argv[1]
img = Image.open(img_path)
decoded = decode(img)
if not decoded:
    raise SystemExit("Nenhum QR code encontrado na imagem")

text = decoded[0].data.decode()
print("URI encontrada:", text)

m = re.search(r"secret=([A-Za-z0-9]+)", text)
if m:
    secret = m.group(1)
    print("Secret extraída:", secret)
else:
    print("Secret não encontrada na URI")