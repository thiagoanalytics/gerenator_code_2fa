from PIL import Image
from pyzbar.pyzbar import decode

img = Image.open("../qrcode/qrcode_ms.png")
data = decode(img)[0].data.decode()
print(data)  
