# Biblioteker
import bluetooth
import sys
import matplotlib.pyplot as plt
import time


# Variabler

# Bluetooth
TARGET_ADDRESS = "00:06:66:8E:23:CC"  # Vores Bluetooth moduls MAC adresse
channel = 1
buffer = ""

# Accelerometer værdier
accX = 0
accY = 0
accZ = 0

# Om den er kalibreret eller ej
calibrated = False

# Calibrerings værdier
offsetX = 0
offsetY = 0
offsetZ = 0

# Det gemte data der bliver vist i grafer | Graferne er ikke nødvændigt og blev brugt til at udvikle programmet og finde de bedste værdier
savedDataX = []
savedDataY = []
savedDataZ = []

# Point - antal squats/armbøjninger
point = 0

# Høje og lave grænser man skal nå for at få et point
lower_threshold = -145
upper_threshold = 145

# Den fase af den øvelse man er i gang med
exercise_stage = 0

# Sætter graferne op
plt.ion()

fig, axs = plt.subplots(3)

lineX, = axs[0].plot([], [], 'r')
axs[0].set_title("X-retning")

lineY, = axs[1].plot([], [], 'g')
axs[1].set_title("Y-retning")

lineZ, = axs[2].plot([], [], 'b')
axs[2].set_title("Z-retning")

for ax in axs:
    ax.set_xlim(0, 200)
    ax.set_ylim(-400, 400)

plt.show()


# Funktioner

# En funktion der deler værdierne fra Bluetooth i de tre forskellige variabler
def parseData(tempData):
    global accX, accY, accZ

    list = tempData.split()

    accX = int(list[-3])
    accY = int(list[-2])
    accZ = int(list[-1])

# Gemmer data til senere
def recordData(newX, newY, newZ):
    savedDataX.append(newX)
    savedDataY.append(newY)
    savedDataZ.append(newZ)

# Ekskludere værdierne uden for smallest og largest
def exclude(n, smallest, largest):
    if n > smallest and n < largest:
        return n
    else:
        return 0


# Den vigtige del af programmet
try:
    # Forbind til Bluetooth og stop hvis der ikke er svar inde for 20 sekunder
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((TARGET_ADDRESS, channel))
    sock.settimeout(20.0)

    # Main loop
    while True:
        try:
            # Modtag data fra Bluetooth
            data = sock.recv(1024).decode()

            # Gentag for hver værdi man for fra Bluetooth
            for char in data:

                # Hver sæt a xyz koordinater slutter med "\n" så den køre kun efter hvert sæt
                if char == "\n":

                    # Formater data
                    parseData(buffer)
                    buffer = ""

                    # Hvis den ikke er kalibreret
                    if calibrated == False:

                        # Skriv til brugeren at der kalibreres, og at de skal holde stille
                        print("Starter kalibrering, hold modulet stille i fem sekunder")
                        time.sleep(2)

                        # Gem de stillestående værdier så man ved hvor meget man skal kompensere for
                        offsetX = accX
                        offsetY = accY
                        offsetZ = accZ

                        # Sæt kalibrering til at være sand så man ikke gør det igen
                        calibrated = True

                        time.sleep(2)
                    
                    # Rund alle værdierne ned til nærmeste af factor | Altså 5 i dette tilfælde
                    factor = 5

                    accX = int((accX - offsetX)/factor)*factor
                    accY = int((accY - offsetY)/factor)*factor
                    accZ = int((accZ - offsetZ)/factor)*factor
                    
                    # Fjern alle værdi der er under -55 og over 55
                    accX = exclude(accX,-55,55) * 4
                    accY = exclude(accY,-55,55) * 4
                    accZ = exclude(accZ,-55,55) * 4

                    # Gem det nye data
                    recordData(accX, accY, accZ)

                    # Hvis det nyeste data er over eller under grænserne | Gå op i point hvis man færdigøre en øvelse
                    if savedDataX[-1] <= lower_threshold and exercise_stage == 0:
                        exercise_stage = 1
                    elif savedDataX[-1] >= upper_threshold and exercise_stage == 1:
                        exercise_stage = 0
                        point += 1
                        print("Antal point: " + str(point))

                    # Slet data der er mere en 200 gammelt
                    if len(savedDataX) > 200:
                        savedDataX.pop(0)
                        savedDataY.pop(0)
                        savedDataZ.pop(0)

                    # Indsæt værdier i graferne
                    x_axis = range(len(savedDataX))

                    lineX.set_data(x_axis, savedDataX)
                    lineY.set_data(x_axis, savedDataY)
                    lineZ.set_data(x_axis, savedDataZ)

                    for ax in axs:
                        ax.set_xlim(0, 200)
                    
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                # Hvis man ikke har et helt sæt af data så gem det til senere
                else:
                    buffer += char
        
        # Stop hvis man mister Bluetooth forbindelse
        except bluetooth.btcommon.BluetoothError:
            print("No data received (timeout).")

# Stop programmet hvis brugeren stopper det | Default er ctrl + c, men det kan ændres
except KeyboardInterrupt:
    print("\nStopped by user.")

# Hvis der går noget galt mens man prøver at forbinde til Bluetooth så skriv fejlen
except bluetooth.btcommon.BluetoothError as err:
    print("Bluetooth Error:", err)
    sys.exit(1)

# Når man stopper programmet så luk for Bluetooth forbindelsen
finally:
    try:
        sock.close()
        print("\nSocket closed.")
    except:
        pass
