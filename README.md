# **ESP-8266-particle-sensor**
IoT air quality tracking with the Shinyei PPD42-ns sensor or the Samyoung DSM501A.

# Goal

Create an IoT particulate matter sensor for measuring and tracking air quality.

# Background

After living in the Bay Area and Isla Vista, and working in a nasty solar cell factory, 
my respiratory system was effected and I became interested in measuring air quality.  
There are a lot of good air quality sensors out there -- that cost $5k.  Even the cheapest ones 
cost $300 if you want to connect them to a computer to save the data, and they aren't even 
Wifi-enabled.

I set out to make an IoT dust concentration sensor, that can be used for air purifiers, 
in industry, and households, and in our dirty cities, to check the quality of the air by 
measuring particulate matter.
This is that project.

# Subfolders

The NodeMCU folder uses only a NodeMCU Devkit board and the particle sensor, which is the 
minimal cost and parts without custom building a PCB.

The Arduino folder uses an arduino with an ESP-8266 (I'm using model ESP01).

# Task list

* get P2 particle size working with NodeMCU devkit.  Currently it reads lower than P1 regardless 
of setpoint

* create calibration curves for different particle sizes for P2, especially for 0.5 micron 
using the dylos pro particle counter

* make sure data gets sent from NodeMCU without memory issues -- was crashing from running 
out of memory before