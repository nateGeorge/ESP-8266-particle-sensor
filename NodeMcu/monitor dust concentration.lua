currentDust = {}
skDisconB4Send = false
local P1pin = 7
local du = 0
local sampleTime = 30000
local lowPulseOccupancy = 0
local startTime = tmr.now()
local pulse1 = tmr.now()
dataSent = true

function measureDust()
    ratio = lowPulseOccupancy/(sampleTime*10) -- LPO in us, sampleTime in ms, ratio is a %.  Divide by 1k, mult by 100
    print('LPO: '..lowPulseOccupancy..', ratio: '..ratio)
    lowPulseOccupancy = 0
    concentration = 1.1*math.pow(ratio,3)-3.8*math.pow(ratio,2)+520*ratio+0.62
    currentDust.P1 = concentration
    currentDust.datetime = tmr.time()
    print('P1 concentration: '..concentration)
    print('time: '..currentDust.datetime)
    gpio.mode(P1pin,gpio.OUTPUT)
    gpio.write(P1pin,gpio.HIGH)
    dofile('sendData - P1.lc')
    print('after dofile')
end

function pin1cb(level)
    du = tmr.now() - pulse1
    print('pin '..P1pin..' du:'..du..', pinlevel: '..level)
    pulse1 = tmr.now()
    if level == 1 then
        gpio.trig(P1pin, "down")
        lowPulseOccupancy = lowPulseOccupancy + du
    else 
        gpio.trig(P1pin, "up")
    end
end

tmr.alarm(4, 2000, 1, function()
    print('checking dataSent: '..tostring(dataSent))
    print('heap: '..node.heap())
    if (dataSent) then
        pulse1 = tmr.now()
        du = 0
        dataSent = false
        skDisconB4Send = false
        print('starting measurement')
        gpio.mode(P1pin,gpio.INT) --P1 output, 1um
        gpio.trig(P1pin, "down", pin1cb)
        tmr.alarm(3, sampleTime, 0, function() measureDust() end)
    elseif (skDisconB4Send == true) then
        print('trying to resend...')
        skDisconB4Send = false
        collectgarbage()
        dofile('sendData - P1.lc')
    end
end)
