-- being connected to a wifi network severely effects the measurement,
-- making the concentration reading much higher
wifi.sta.disconnect()
dustData = {}
dataCounter = 1
mvgAvgPeriod = 6 -- take average every 6 readings and send to cloud
P1pin = 0
P2pin = 1
P2setPin = 8
du = 0
sampleTime = 15000 -- 15 seconds
lowPulseOccupancy = 0
gpio.mode(P1pin,gpio.INT) -- P1 output, 1um
gpio.mode(P2pin,gpio.INT) -- P2 output, variable um, ~0.5um with 10k resistor between P2 setpoint and GND

function measureDust()
  -- LPO in us, sampleTime in ms, ratio is a %.  Divide by 1k, mult by 100
  ratio = lowPulseOccupancy/(sampleTime*10)
  print('LPO: '..lowPulseOccupancy..', ratio: '..ratio)
  lowPulseOccupancy = 0
  if readPin == P1pin then
    P1concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio
    print('P1 concentration: '..P1concentration)
    dustData
    readPin = P2pin
    pulse1 = tmr.now()
    du = 0
    gpio.trig(readPin, "down", pin1cb)
  elseif readPin == P2pin then
    P2concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio
    print('P2 concentration: '..P2concentration)
    readPin = P1pin
    pulse1 = tmr.now()
    du = 0
    gpio.trig(readPin, "down", pin1cb)
    dustData[dataCounter] = [P1concentration, P2concentration]
    counter = counter + 1
    if (counter > mvgAvgPeriod) then
        counter = 0
        sendToTS = require("sendToTS")
        dataToSend = {}
        dataToSend[1] = {'0.5um', 0}
        dataToSend[2] = {'1um', 0}
        for num, data in ipairs(dustData) do
            dataToSend[1][2] = dataToSend[1][2] + data[2]
            dataToSend[2][2] = dataToSend[2][2] + data[1]
        end
        dataToSend[1][2] = dataToSend[1][2]/mvgAvgPeriod
        dataToSend[2][2] = dataToSend[2][2]/mvgAvgPeriod
        sendToTS.sendData('dust keys', dataToSend, false, true)
    end
  end
end

function pin1cb(level)
  du = tmr.now() - pulse1
  print('pin '..readPin..' du:'..du..', pinlevel: '..level)
  pulse1 = tmr.now()
  if level == 1 then
    gpio.trig(readPin, "down")
    lowPulseOccupancy = lowPulseOccupancy + du
  else 
    gpio.trig(readPin, "up")
  end
end

readPin = P1pin
gpio.trig(readPin, "down", pin1cb)
pulse1 = tmr.now()

tmr.alarm(3, sampleTime, 1, function() measureDust() end)
