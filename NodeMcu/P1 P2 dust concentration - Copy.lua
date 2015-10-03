-- being connected to a wifi network severely effects the measurement,
-- making the concentration reading much higher
wifi.sta.disconnect()
P1pin = 0
P2pin = 1
du = 0
sampleTime = 30000
lowPulseOccupancy = 0
gpio.mode(P1pin,gpio.INT) -- P1 output, 1um
gpio.mode(P2pin,gpio.INT) -- P2 output, 0.5um

function measureDust()
  -- LPO in us, sampleTime in ms, ratio is a %.  Divide by 1k, mult by 100
  ratio = lowPulseOccupancy/(sampleTime*10)
  print('LPO: '..lowPulseOccupancy..', ratio: '..ratio)
  lowPulseOccupancy = 0
  if readPin == P1pin then
    -- concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62 -- formula for shinyei PPD42NS
    concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62 -- formula for DSM501A
    print('P1 concentration: '..concentration)
    readPin = P2pin
    pulse1 = tmr.now()
    du = 0
    gpio.trig(readPin, "down", pin1cb)
  elseif readPin == P2pin then
    -- concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62 -- for PPD42NS
    concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62 -- formula for DSM501A
    print('P2 concentration: '..concentration)
    readPin = P1pin
    pulse1 = tmr.now()
    du = 0
    gpio.trig(readPin, "down", pin1cb)
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
