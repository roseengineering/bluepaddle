

# Bluetooth BLE CW / Morse Code Paddle Controller

This repo contains a BLE implementation of a CW Paddle
in Micropython.  Specifically it is designed to be used
on a ESP32 microcontroller with Micropython ESP-IDF v4.x firmware 
for BLE support.

### How to Use

Connect the dit switch of the paddle (or the tip of the TRS connector)
of the paddle to the ESP32's GPIO13 pin.  Next connect the dah switch 
of the paddle (or the ring of the TRS connector) to ESP32's GPIO12 pin.
And of course connect paddle common to ESP32's GND pin.

Set the mac address of your ESP32 Bluetooth device in client.py.
Install the bluepy python3 library on your host computer using 
for example pip.

Run client.py on your host computer.  It will connect to your paddle
and print the switch contacts as they change.

### BLE Service and Characteristics

bluepaddle uses it own BLE service and characteristics.  (I chose
not to use HID over BLE.)

The CW Paddle service is "12d32121-b01c-11ea-91d2-3fd36973e665".

The CW Paddle characteristic is "12d32122-b01c-11ea-91d2-3fd36973e665".
The host can read the paddle switch status or be notified of it.
The status consists of one byte.  Bit 0 is set when the dit switch makes
contact.  Bit 1 is set when the dah switch makes contact.


