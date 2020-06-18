
from micropython import const
from machine import Pin
import time
import struct
import bluetooth


# gatt advertising

_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_APPEARANCE = const(0x19)

def advertising_payload(limited_disc=False, br_edr=False, name=None, 
                        services=None, appearance=0):
    payload = bytearray()
    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value
    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + 
                         (0x18 if br_edr else 0x04)))
    if name:
        _append(_ADV_TYPE_NAME, name)
    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)
    _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))
    return payload

# gatt uart service


_KEY_UUID = bluetooth.UUID("12d32121-b01c-11ea-91d2-3fd36973e665")
_KEY_TX = (
    bluetooth.UUID("12d32122-b01c-11ea-91d2-3fd36973e665"),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY
)
_KEY_SERVICE = (
    _KEY_UUID,
    (_KEY_TX,)
)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

class BLEKey:
    def __init__(self, ble, name="bluekey"):
        self._connections = set()
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._tx_handle,),) = self._ble.gatts_register_services((_KEY_SERVICE,))
        self._payload = advertising_payload(
            name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            self._advertise()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def write(self, data):
        self._ble.gatts_write(self._tx_handle, data)
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)


# paddle

def latch2(p0, p1):
    prev = None
    while True:
        a = 3 ^ ((p0.value() << 1) | p1.value())
        if a == prev: return a
        time.sleep_us(10)
        prev = a

class Key:
    # red wire is tip or dit: left paddle if right handed
    # white wire is ring or dah: right paddle if right handed

    def __init__(self, pin_dah, pin_dit):
        self._dah = Pin(pin_dah, Pin.IN, Pin.PULL_UP)
        self._dit = Pin(pin_dit, Pin.IN, Pin.PULL_UP)
        self._prev = None

    def callback(self):
        state = latch2(self._dah, self._dit)
        if state != self._prev:
            self._prev = state
            if self._handler:
                self._handler(state)

    def irq(self, handler):
        self._handler = handler


# gpio pins

PIN_DIT = 13
PIN_DAH = 12

# initialize


def main():
    def onchange(state):
        data = bytes([state])
        bk.write(data)

    ble = bluetooth.BLE()
    bk = BLEKey(ble)
    key = Key(PIN_DAH, PIN_DIT)
    key.irq(handler=onchange)
    while True:
        key.callback()
 

main()

