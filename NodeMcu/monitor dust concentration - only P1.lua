i2c.setup(0, 3, 4, i2c.SLOW)
lcd = dofile("lcd1602.lua")()
lcd.put(lcd.locate(0, 0), "Starting up...")

P1pin = 7
P2pin = 6
P2setPin = 8
du = 0
sampleTime = 30000
lowPulseOccupancy = 0
startTime = tmr.now()
pulse1 = tmr.now()
gpio.mode(P1pin,gpio.INT) --P1 output, 1um
gpio.mode(P2pin,gpio.INT) --P2 output, variable um

function setP2thresh(particleSize)
  p2DutyCycle = particleSize/3.3*1023
  pwm.setup(P2setPin,1000,p2DutyCycle)
  pwm.start(P2setPin)
end

function measureDust()
  ratio = lowPulseOccupancy/(sampleTime*10) -- LPO in us, sampleTime in ms, ratio is a %.  Divide by 1k, mult by 100
  print('LPO: '..lowPulseOccupancy..', ratio: '..ratio)
  lowPulseOccupancy = 0
  if readPin == P1pin then
    concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62
    print('P1 concentration: '..concentration)
    lcd.put(lcd.locate(0, 0), "Concentration:")
    lcd.put(lcd.locate(1, 0), string(math.floor(concentration+0.5)))
    --readPin = P2pin
    pulse1 = tmr.now()
    du = 0
    gpio.trig(readPin, "down", pin1cb)
  elseif readPin == P2pin then
    concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62
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

tmr.alarm(3, sampleTime, 1, function() measureDust() end)
