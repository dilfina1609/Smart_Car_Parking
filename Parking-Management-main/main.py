import serial

ser = serial.Serial('COM6', 9600, timeout=2)  

while True:

    data = ser.readline().decode().strip()
    

    print(data)
