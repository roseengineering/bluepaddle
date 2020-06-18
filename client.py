
from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, chandle):
        self.chandle = chandle
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, chandle, data):
        if self.chandle == chandle:
            data = ord(data)
            print("dah" if data & 2 else "   ", 
                  "dit" if data & 1 else "")

mac = 'cc:50:e3:80:a2:aa'
service_uuid = "12d32121-b01c-11ea-91d2-3fd36973e665"
char_uuid = "12d32122-b01c-11ea-91d2-3fd36973e665"

per = btle.Peripheral(mac, addrType=btle.ADDR_TYPE_PUBLIC)
svc = per.getServiceByUUID(service_uuid)
ch = svc.getCharacteristics(char_uuid)[0]
chandle = ch.getHandle()

per.setDelegate(MyDelegate(chandle))
print('waiting')
while True:
    per.waitForNotifications(1.0)

