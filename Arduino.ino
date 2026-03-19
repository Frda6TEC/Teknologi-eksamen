#include <SoftwareSerial.h>
// receive og transmit der bruges så det er muligt at modtage og sende information til og fra bluetooth modulet
int bluetoothRx =3;
int bluetoothTx =2;

SoftwareSerial bluetooth(bluetoothTx, bluetoothRx);
char data;

const int xpin = A3;                  // x-axis of the accelerometer

const int ypin = A5;                  // y-axis

const int zpin = A4;                  // z-axis (only on 3-axis models)
int hej=1;
String komma =String(" ");

void setup() {
    Serial.begin(9600);
    bluetooth.begin(115200); // pga røde model
}

void loop() {

    // læser og skriver alle de målte x-, y- og z-værdier fra accelerometer i serial monitor 

    Serial.print(analogRead(xpin));
    Serial.print("\t");
    Serial.print(analogRead(ypin));
    Serial.print("\t");
    Serial.print(analogRead(zpin));
    Serial.println();

    // tjekker om bluetooth er der 
    if(bluetooth.available()){

        data = bluetooth.read();

        Serial.print("bluetooth on    ");
        Serial.print("Received: ");
        Serial.println(data);


        Serial.println("sender nu");



        //  printer alle mållingerne fra accelerometeret og printer det på bluetooth modulet, som sender det videre til personen der er forbundet
        bluetooth.print(analogRead(xpin));
        bluetooth.print(" ");
        bluetooth.print(analogRead(ypin));
        bluetooth.print(" ");
        bluetooth.print(analogRead(zpin));
        bluetooth.println();
    }
}