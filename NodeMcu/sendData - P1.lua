file.open("keys")
PuKey = file.readline()
PrKey = file.readline()
file.close()
local sendURL = '/input/'..PuKey..PrKey
local counter = 0
local success = nil
local response = nil
local address = "54.86.132.254" --data.sparkfun.com
local conn, msg, sk

local connectFunk = function()
    counter = counter + 1
    print("connecting wifi")
    if (wifi.sta.status()==5) then
        print("wifi connected")
        sk = net.createConnection(net.TCP, 0)
        sk:on("reconnection", reFunk)
        sk:on("disconnection", discoFunk)
        sk:on("receive", recFunk)
        sk:on("connection", conFunk)
        sk:connect(80, address)
        tmr.stop(1)
    elseif (wifi.sta.status()~=1 or wifi.sta.status()~=5) then
        wifi.sta.connect()
    elseif (wifi.sta.status()==1 and counter > 20) then
        wifi.sta.disconnect()
        wifi.sta.connect()
    end
    end


local reFunk = function(conn)
            print("socket reconnected")
        end

local discoFunk = function(conn)
            print('socket disconnected')
            sk = nil
            tmr.alarm(6, 1000, 0, sucFunk)
        end

local sucFunk = function()
                if (success ~= nil) then
                    dataSent = true
                    collectgarbage()
                elseif (response == nil) then
                    skDisconB4Send = true
                    collectgarbage()
                elseif (response ~= nil) then
                    print(response)
                    skDisconB4Send = true
                    collectgarbage()
                end
            end

local recFunk = function(conn, msg)
            response = msg
            print(msg)
            print('heap1: '..node.heap())
            _,_,success = string.find(msg, "(success)")
            if (success==nil) then
                print('some data not sent')
                file.open('unsentData','a+')
                file.writeline(currentDust.P1..','..currentDust.datetime)
                file.close()
            end
            wifi.sleeptype(1)
            wifi.sta.disconnect()
            sk:close()
            if (success~=nil) then
                dataSent = true
                skDisconB4Send = false
                collectgarbage()
            end
            end

local conFunk = function(conn)
            print("socket connected")
            print(node.heap())
            print("sending...")
            print(node.heap())
            print("before send heap: "..node.heap())
            conn:send("GET "..sendURL..currentDust.P1..'&datetime='..currentDust.datetime.." HTTP/1.1\r\nHost: "..address.."Connection: close\r\nAccept: */*\r\nUser-Agent: Mozilla/4.0 (compatible; ESP8266;)\r\n\r\n", sendFunk)
            print("after send heap: "..node.heap())
            collectgarbage()
        end

local sendFunk = function() 
                print("sent:")
                print("GET "..sendURL..currentDust.P1..'&datetime='..currentDust.datetime.." HTTP/1.1\r\nHost: "..address.."Connection: close\r\nAccept: */*\r\nUser-Agent: Mozilla/4.0 (compatible; ESP8266;)\r\n\r\n")
            end

if (currentDust.P1~=nil) then
    if (wifi.sta.status()~=5) then
        wifi.sleeptype(0)
        wifi.setmode(1)
        wifi.sta.connect()
    end
    
    tmr.alarm(1, 1000, 1, connectFunk)
end
