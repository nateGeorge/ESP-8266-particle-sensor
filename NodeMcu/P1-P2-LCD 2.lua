--functions
function pin1cb(level)
  du = tmr.now() - pulse1
  print('pin '..tostring(readPin)..' du:'..tostring(du)..', pinlevel: '..tostring(level))
  pulse1 = tmr.now()
  if level == 1 then
    gpio.trig(readPin, "down")
    lowPulseOccupancy = lowPulseOccupancy + du
  else 
    gpio.trig(readPin, "up")
  end
end

-- being connected to a wifi network severely effects the measurement,
-- making the concentration reading much higher
wifi.sta.disconnect()
tmr.delay(1000) -- first second or so usually gives a very high number

-- load EMA periods
dofile('EMAsetup.lua')
-- load regime settings
dofile('AQregimes.lua')
useRegime = 1

-- LCD settings
i2c.setup(0, 3, 4, i2c.SLOW) -- SDA, SCL 3, 4
lcd = dofile("lcd1602.lua")()
lcd.put(lcd.locate(0, 0), "Starting up...")

-- particle monitor settings
P1pin = 7
P2pin = 2
du = 0
sampleTime = 5000 -- in ms, of course
lowPulseOccupancy = 0
firstMeas = true;
gpio.mode(P1pin,gpio.INT) -- P1 output, 1um
--gpio.mode(P2pin,gpio.INT) -- P2 output, 0.5um

function measureDust()
  print(node.heap())
  -- LPO in us, sampleTime in ms, ratio is a %.  Divide by 1k, mult by 100
  ratio = lowPulseOccupancy/(sampleTime*10)
  print('LPO: '..tostring(lowPulseOccupancy)..', ratio: '..tostring(ratio))
  lowPulseOccupancy = 0
  if readPin == P1pin then
    print(node.heap())
    concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio

    -- calculate moving average
    if firstMeas then
        avg1um = concentration
        firstMeas = false
    else
        for i, cutoff in ipairs(cutoffs) do
            if avg1um >= cutoff then
                alpha = 2/(periods[i] + 1);
            end
        end
        avg1um = alpha * concentration + (1-alpha) * avg1um
    end

    -- determine air quality regime
    --judgement = regimes[useRegime][2][1][2]]; -- worst regime if nothing else matches
    for i, regime in ipairs(regimes[useRegime][1]) do
        if avg1um >= regime then
            judgement = regimes[useRegime][2][i];
        end
    end
    print('P1 concentration: '..tostring(concentration))
    print('average: '..tostring(avg1um))
    print('regime: '..judgement)
    lcd.clear()
    lcd.put(lcd.locate(0, 0), judgement)
    lcd.put(lcd.locate(1, 0), tostring(math.floor(avg1um + 0.5)))
    --readPin = P2pin
    pulse1 = tmr.now()
    du = 0
    gpio.trig(readPin, "down", pin1cb)
  --elseif readPin == P2pin then
  --  concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62
  --  print('P2 concentration: '..concentration)
  --  readPin = P1pin
  --  pulse1 = tmr.now()
  -- du = 0
  --  gpio.trig(readPin, "down", pin1cb)
  end
end

readPin = P1pin
gpio.trig(readPin, "down", pin1cb)
pulse1 = tmr.now()

tmr.alarm(3, sampleTime, 1, function() measureDust() end)
