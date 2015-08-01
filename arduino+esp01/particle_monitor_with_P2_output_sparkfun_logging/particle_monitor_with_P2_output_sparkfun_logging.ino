/* Grove - Dust Sensor Demo v1.0
 Interface to Shinyei Model PPD42NS Particle Sensor
 Original Program by Christopher Nafis 
 Written April 2012
 Updated by Nathan George, 2015
 
 http://www.seeedstudio.com/depot/grove-dust-sensor-p-1050.html
 http://www.sca-shinyei.com/pdf/PPD42NS.pdf
 http://www.samyoungsnc.com/products/3-1%20Specification%20DSM501.pdf
 
 This is using either the samyoung 501A or shinyei PPD42ns
 perspective is looking down at the dust sensor
 Pin 1 (far right wire)  => Arduino GND
 Pin 2 (second from right) => Arduino Pin 9
 Pin 3 (middle)    => Arduino 5VDC
 Pin 4 (second from left) => Arduino Digital Pin 8; I think P1 and P2 may be switched on DSM501A 
 Pin 5 (far left) => Arduino Pin 5
 make sure you have a PWM -> analog converted in between pin 5 and the sensor
 as shown here: http://provideyourown.com/2011/analogwrite-convert-pwm-to-voltage/
 using 22k resistor and 10uF capacitor works well
 
 fan (using same PWM => analog conversion)
 red => pin 6
 black => GND
 
 ESP8266 wifi chip
 VCC and CHIP_PD => 3.3V vcc from voltage converter
 GND => GND
 RX => 2
 TX => 3
 
Dylos Air Quality Chart - Small Count Reading (0.5 micron)+

3000 +     = VERY POOR
1050-3000  = POOR
300-1050   = FAIR
150-300    = GOOD
75-150     = VERY GOOD
0-75       = EXCELLENT

1 micron+

1000 +     = VERY POOR
350-1000   = POOR
100-350    = FAIR
50-100     = GOOD
25-50      = VERY GOOD
0-25       = EXCELLENT
 */
#include<SoftwareSerial.h>



float threshDuty = 25; // roughly sets threshhold voltage for P2 to (26 (25.5 exactly) for 0.5V for detection of 0.5u particles)
// on this particular shinyei one I have it seems like 70 lines up with P1 concentration of 1 micron, so assuming an offset of 0.37V for P2
// so 0.5 micron should be a duty cycle of 44
// on the dsm501A it seems different

int setPin = 5; // setting voltage for P2 detection threshhold, volatage = particle size in micron
int P1pin = 8;
int P2pin = 9;
int fanPin = 6; // for controlling power of fan
int pin = P1pin;
int i = 1; //counter for switching between P1 and P2
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000;//sample 30s ;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;
char c;
String msg = "";

SoftwareSerial wifiSerial(2, 3); // connected to TX, RX on wifi chip

void setup() {
  pinMode(setPin, OUTPUT);
  // analogWrite(setPin, threshDuty); // 51 should be 1 um for P2, this will set the input P2 voltage for particle detection size
  Serial.begin(9600);
  wifiSerial.begin(9600);
  pinMode(P1pin,INPUT);
  pinMode(P2pin,INPUT);
  starttime = millis();//get the current time;
}

void loop() {
  
  duration = pulseIn(pin, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;


  
   if ((millis()-starttime) > sampletime_ms)
  {
    ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Integer percentage 0=>100
    //concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve for 1 um particles, shinyei PPD42ns
    //concentration = 0.1187*ratio - 0.0865; // mg/m3 using spec sheet curve for DSM501A
    concentration = 620.61*ratio/10; // particles/0.01ft3 for DSM501A, /10 to correlate with dylos sensor
    if (i == 1) {
      analogWrite(setPin, threshDuty); // turns on P2 detection pin, have to wait 51 should be 1 um for P2, this will set the input P2 voltage for particle detection size. with 22kOhm and 10uF PWM power converter, this should take about a second
      pin = P2pin;
      Serial.println("P1: " + String(concentration));
      Serial.println("P1 ratio: " + String(ratio));
      wifiSerial.println("currentDust.P1=" + String(roundf(concentration)));
      delay(1100); // wait for the ESP8266 to catch up with input, and for P2 voltage threshold to plateau
      while (wifiSerial.available()){
        c = wifiSerial.read();
        msg += c;
      }
      Serial.println(msg);
      msg = "";
    }
    else {
      pin = P1pin;
      analogWrite(setPin, 0);
      Serial.println("P2: " + String(concentration));
      Serial.println("P2 ratio: " + String(ratio));
      wifiSerial.println("currentDust.P2=" + String(roundf(concentration)));
      delay(500); // wait for esp8266 to process input, and make sure don't garble P2 with dofile('... below
      while (wifiSerial.available()){
        c = wifiSerial.read();
        msg += c;
      }
      Serial.println(msg);
      msg = "";
      wifiSerial.println("dofile('sendData.lua')");
      while (wifiSerial.available()){
        c = wifiSerial.read();
        msg += c;
      }
      Serial.println(msg);
      msg = "";
      i = 0;
    }
    lowpulseoccupancy = 0;
    starttime = millis();
    i++;
  }

}
