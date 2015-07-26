/* Grove - Dust Sensor Demo v1.0
 Interface to Shinyei Model PPD42NS Particle Sensor
 Program by Christopher Nafis 
 Written April 2012
 
 http://www.seeedstudio.com/depot/grove-dust-sensor-p-1050.html
 http://www.sca-shinyei.com/pdf/PPD42NS.pdf
 
 JST Pin 1 (Black Wire)  => Arduino GND
 JST Pin 3 (Red wire)    => Arduino 5VDC
 JST Pin 4 (Yellow wire) => Arduino Digital Pin 8
 
Dylos Air Quality Chart - Small Count Reading (0.5 micron)+

3000 +     = VERY POOR
1050-3000  = POOR
300-1050   = FAIR
150-300    = GOOD
75-150     = VERY GOOD
0-75       = EXCELLENT
 */
#include<SoftwareSerial.h>

int setPin = 3; // setting voltage for P2 detection threshhold, volatage = particle size in micron

float threshDuty = 36; // roughly sets threshhold voltage for P2 to (26 (25.5 exactly) for 0.5V for detection of 0.5u particles)
// on this particular one it seems like 70 lines up with P1 concentration of 1 micron, so assuming an offset of 0.37V for P2
// so 0.5 micron should be a duty cycle of 44

int P2pin = 8;
int P1pin = 9;
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

SoftwareSerial wifiSerial(5, 6); // RX, TX

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
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve for 1 um particles
    if (i == 1) {
      analogWrite(setPin, threshDuty); // turns on P2 detection pin, have to wait 51 should be 1 um for P2, this will set the input P2 voltage for particle detection size. with 22kOhm and 10uF PWM power converter, this should take about a second
      pin = P2pin;
      Serial.println("P1:" + String(concentration));
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
      Serial.println("P2:" + String(concentration));
      wifiSerial.println("currentDust.P2=" + String(roundf(concentration)));
      delay(500); // wait for esp8266 to process input, and make sure don't garble P2 with dofile('... below
      while (wifiSerial.available()){
        c = wifiSerial.read();
        msg += c;
      }
      Serial.println(msg);
      msg = "";
      wifiSerial.println("dofile('sendData.lc')");
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
