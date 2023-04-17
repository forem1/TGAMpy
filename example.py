import time
from TGAMpy.TGAMpy import TGAM

module = TGAM()

print(module.connect("COM10", timeout=5))

while True:
    module.read()
    print("Attention: ", module.eAttention)
    print("Meditation: ", module.eMeditation)
    print(module.raw_data)

    time.sleep(1)