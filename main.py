import bluetooth
import sys

TARGET_ADDRESS = "00:06:66:8E:23:CC"  # RN-41 MAC address
channel = 1
buffer = ""

currentX = 0
currentY = 0
currentZ = 0

offsetX = 0
offsetY = 0
offsetZ = 0

calibrated = False

def parseData(tempData):
    global currentX
    global currentY
    global currentZ

    list = tempData.split()

    currentX = int(list[-3])
    currentY = int(list[-2])
    currentZ = int(list[-1])

    

#parseData("123 456 789")

try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((TARGET_ADDRESS, channel))
    sock.settimeout(20.0)

    print("Starter kalibrering, hold modulet stille i fem sekunder")

    while True:
        sock.send("hello")
        #print("Sent hello")

        try:
            data = sock.recv(1024).decode()

            for char in data:
                if char == "\n":

                    parseData(buffer)

                    if calibrated == False:
                        offsetX = currentX
                        offsetY = currentY
                        offsetZ = currentZ

                        calibrated = True
                    

                    currentX = currentX - offsetX
                    currentY = currentY - offsetY
                    currentZ = currentZ - offsetZ
                    
                    print(currentX)
                    print(currentY)
                    print(currentZ)
                    print("")


                else:
                    buffer += char
        except bluetooth.btcommon.BluetoothError:
            print("No data received (timeout).")

except KeyboardInterrupt:
    print("\nStopped by user.")

except bluetooth.btcommon.BluetoothError as err:
    print("Bluetooth Error:", err)
    sys.exit(1)

finally:
    try:
        sock.close()
        print("\nSocket closed.")
    except:
        pass


