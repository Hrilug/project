import socket
import serial

ser = serial.Serial('COM7',115200)
ser.timeout = 0.001
host = "127.0.0.1"
port = 1000
s = socket.socket()
s.connect((host, port))
s.send("1234".encode("utf8"))

while True:
    if ser.inWaiting() > 0:
        val=ser.readline()
        print(val)
        s.send(val)
