/* Grove - Dust Sensor v3.0
 added LED that responds to moving average
 Interface to Shinyei Model PPD42NS Particle Sensor
 
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

Dylos Air Quality Chart (1 micron)+
1000+ = VERY POOR
350 - 1000 = POOR
100 - 350 = FAIR
50 - 100 = GOOD
25 - 50 = VERY GOOD
0 - 25 = TOTALLY EXCELLENT, DUDE!

with a 64KB eeprom, should be able to store 128 hours (5 1/3 days) of 30-second data.

a 2000-part array of unsigned ints for times in seconds and dust concentrations 
(about 16 hours of data) takes 8KB

can only store almost 5 hours of data on internal storage

assume have about 1KB dynamic memory, 1KB eeprom.  That's 500 data points

for now store 2 hours high-resolution data

if store 255 points of data with 3-min resolution, takes only 800KB.  
That will cover 12.75 hours

 */
#include <SoftwareSerial.h>
#include <MemoryFree.h>
#include <stdlib.h>

const byte redpin = 4; // select the pin for the red LED
const byte greenpin = 5 ;// select the pin for the green LED
const byte bluepin = 6; // select the pin for the blue LED

const byte numReadings = 6;     // moving average period, synced with 3-min resolution for now
const unsigned int storageArraySize = 10; // size of 3-min resolution data 
unsigned int storageCounter = 0; // counter for position in storage array

float readings[numReadings];      // the readings from the analog input

//unsigned int storageArray[storageArraySize]; // storage array for long-term data; can store about 24hrs of data in 1KB

unsigned int index = 0;                  // the index of the current reading
float total = 0;                  // the running total
float average = 0;                // the average

bool ledON = 0;                // turn LED on or off
bool timeSet = false;          // whether time has been synced between phone and dust sensor
unsigned long currentEpochTime;
String message;                // string to store incoming message from serialWifi


const byte pin = 8; // yellow cable (P1 pin, second from left on board)
unsigned long duration;
unsigned long startTime_ms;
unsigned long sampleTime_ms = 30000;//sample for 30s
unsigned long lastAvgTime_ms; //timestamp of the last moving average of readings
unsigned long lowPulseOccupancy = 0;
float ledSignal = 0;
float ratio = 0;
float concentration = 0;
bool firstTime = true;
int firstTimeCounter = 1;
bool connectSuccess = false;

#define SSID "your network name goes here"
#define PASS "network password here"
#define IP "54.86.132.254" // data.sparkfun.com

String PrKEY = "sparkfun private key";
String PuKEY = "sparkfun public key";
String GET = "GET /input/" + PuKEY + "?private_key=" + PrKEY + "&1um_particle_concentration=";

// for converting concentration as a float to a string for posting to the net
String stringVal = "";
char charVal[10];

char c;
String serialString;

bool printToSerial = true;

SoftwareSerial wifiSerial(2, 3); // RX, TX


void setup() {
  
  wifiSerial.begin(9600);
  
  if (printToSerial) {Serial.begin(9600);}
  
  wifiSerial.setTimeout(15000);
  
  while (!connectSuccess) {
  connectSuccess = connectWiFi();
  }
  delay(7000); // need to wait for power to drop from wifi board, otherwise sucks juice from the 5V one

  // initialize all the readings ande averages to 0: 
  for (int thisReading = 0; thisReading < numReadings; thisReading++)
    readings[thisReading] = 0;
  
  pinMode(redpin, OUTPUT);
  pinMode(bluepin, OUTPUT);
  pinMode(greenpin, OUTPUT);
  pinMode(8,INPUT);
  
  if (printToSerial) {
    Serial.println("freeMemory()=" + String(freeMemory()));
    Serial.println("starting measurement...");
  }
  
  startTime_ms = millis();//get the current time in milliseconds;
  
  
}

void loop() {
  duration = pulseIn(pin, LOW);
  lowPulseOccupancy = lowPulseOccupancy+duration;

  if ((millis()-startTime_ms) >= sampleTime_ms)//if the sample time has been exceeded
  {
    ratio = lowPulseOccupancy/(sampleTime_ms*10.0);  // Integer percentage 0=>100; divide by 1000 to convert us to ms, multiply by 100 for %, end up dividing by 10
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve for shinyei PPD42ns
    if (printToSerial) {
      Serial.println("Concentration: " + String(concentration));
      Serial.println("freeMemory()=" + String(freeMemory()));
    }
    // 3-min moving average:
    // subtract the last reading:
    total = total - readings[index];         
    // read from the sensor:  
    readings[index] = concentration; 
    //Serial.println(readings[index]);
    // add the reading to the total:
    total = total + readings[index];       
    // advance to the next position in the array:  
    index++;
    
    dtostrf(concentration, 4, 2, charVal);
    stringVal = "";
    //convert chararray to string
    for(int i=0; i<sizeof(charVal); i++)
    {
      stringVal+=charVal[i];
    }
    
    updateData(stringVal.substring(0,sizeof(stringVal)+1)); // think I had to do this because it wasn't converting to a string correctly or something...
    delay(7000); // need to wait for power to drop from wifi board, otherwise sucks juice from the 5V one

    // calculate the average:
    average = total / numReadings;
    //Serial.println(average);
    
    // if we're at the end of the array...
    /*if (index >= numReadings) {
      // ...wrap around to the beginning: 
      index = 0;
      // also write to long-term array:
      storageArray[storageCounter] = (unsigned int)average;
      if (printToSerial) {
      Serial.println("ratio");
      Serial.println(ratio);
      Serial.println("average");
      Serial.println(average);
      Serial.println("converted to uint");
      Serial.println(storageArray[storageCounter]);
      }
      lastAvgTime_ms = millis();
      //Serial.println("storage array");
      //Serial.println(storageArray[storageCounter]);
      storageCounter++;
    }*/
     

    // wait until moving average has been completed to use it as a judgement for LED color, otherwise use current value
    if (ledON) {
      if (!firstTime) {
        ledSignal = average;
      }
      else {
        ledSignal = concentration;
        firstTimeCounter += 1;
        if (firstTimeCounter > numReadings) {
          firstTime = false;
        }
      }
      if (ledSignal > 750.0) { // air quality is VERY POOR
        analogWrite(redpin, 255);
        analogWrite(greenpin, 0);
        analogWrite(bluepin, 0);
        //Serial.println("very poor");
      }
      else if (ledSignal > 262.5) { // air quality is POOR
        analogWrite(redpin, 255);
        analogWrite(greenpin, 255);
        analogWrite(bluepin, 0);
        //Serial.println("poor");
      }
      else if (ledSignal > 75) { // air quality is FAIR
        analogWrite(redpin, 255);
        analogWrite(greenpin, 0);
        analogWrite(bluepin, 255);
        //Serial.println("fair");
      }
      else if (ledSignal > 37.5) { // air quality is GOOD
        analogWrite(redpin, 0);
        analogWrite(greenpin, 255);
        analogWrite(bluepin, 255);
        //Serial.println("good");
      }
      else if (ledSignal > 18.75) { // air quality is VERY GOOD
        analogWrite(redpin, 0);
        analogWrite(greenpin, 0);
        analogWrite(bluepin, 255);
        //Serial.println("very good");
      }
      else { // air quality is EXCELLENT (<75)
        analogWrite(redpin, 0);
        analogWrite(greenpin, 255);
        analogWrite(bluepin, 0);
        //Serial.println("excellent");
      }
    }
    else {
      analogWrite(redpin, 0);
      analogWrite(greenpin, 0);
      analogWrite(bluepin, 0);
    }
    lowPulseOccupancy = 0;
    if (printToSerial) {
      Serial.println("starting measurement...");
    }
    startTime_ms = millis(); // reset the timer for sampling at the end so it is as accurate as possible
  }
}

bool initializeConnection() {
    // initialize TCP connection
  String cmd = "AT+CIPSTART=\"TCP\",\"";
  cmd += IP;
  cmd += "\",80";
  sendCmd(cmd);

  if (wifiSerial.find("OK")) {
    if (printToSerial) {Serial.println("connected to external IP successfully.");}
    return true;
  }
  else {
    if (printToSerial) {Serial.println("unable to connect to IP");}
    return false;
  }
}

bool updateData(String data){
  
  int sendTries = 0;
  
  bool initializeSuccess = false;
  connectSuccess = false;
  
  while (!initializeSuccess) {
    sendTries += 1;
    initializeSuccess = initializeConnection();
    if (sendTries == 4) { // use sendtries also as a counter for initilization attemps to save memory
      sendCmd("AT+RST");
      delay(2000);
      while(!connectSuccess) {
        connectWiFi();
      }
      sendTries = 0;
    }
  }
  
  sendTries = 0;
  
  String cmd = GET;
  cmd += data;
  cmd += "\r\n";
  
  // send the data 
  while(true) {
    sendTries += 1;
    if (printToSerial) {Serial.println("requesting to send data...");}
    
    // request to send data
    sendCmd("AT+CIPSEND=" + String(cmd.length()));
    if (wifiSerial.find(">")){
      sendCmd(cmd);
      if(wifiSerial.find("OK")){
        if (printToSerial) {Serial.println("successfully sent!");}
        return true;
      }
      else{
        if (printToSerial) {Serial.println("unable to send...error");}
      }
    }else if (sendTries == 4){
      if (printToSerial) {Serial.println("unable to send data...resetting connection");}
      connectSuccess = false;
      initializeSuccess = false;
      while(!connectSuccess) {
      connectSuccess = connectWiFi();
      }
      while (!initializeSuccess) {
        initializeSuccess = initializeConnection();
      }
      sendTries = 0;
    }
  }
  
}


String readSerial() {
  while(wifiSerial.available() > 0) {
    c = wifiSerial.read();
    serialString += c;
  }
  if (printToSerial) {Serial.println("RECIEVED: " + serialString);}
  return serialString;
}

void sendCmd(String cmd){
  if (printToSerial) {Serial.println("SEND: " + cmd);}
  wifiSerial.println(cmd);
} 
 
bool connectWiFi(){
  if (printToSerial) {Serial.println("connecting wifi...");}
  wifiSerial.println("AT+CWMODE=1");
  if (printToSerial) {Serial.println("SEND: AT+CWMODE=1");}
  if (wifiSerial.find("OK")) {
    if (printToSerial) {Serial.println("set wifi mode as station successfully.");}
  }
  else {
    if (printToSerial) {Serial.println("unable to set wifi mode as station");}
    return false;
  }
  String cmd="AT+CWJAP=\"";
  cmd+=SSID;
  cmd+="\",\"";
  cmd+=PASS;
  cmd+="\"";
  sendCmd(cmd);
  if (wifiSerial.find("OK")) {
    if (printToSerial) {Serial.println("joined network successfully.");}
    return true;
  }
  else {
    if (printToSerial) {Serial.println("unable to join network, check credentials.");}
    return false;
  }
}
