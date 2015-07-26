file.open("keys")
PuKey = file.readline()
PrKey = file.readline()
file.close()
print(PuKey)
print(PrKey)

if (currentDust.P1~=nil) then
    if (wifi.sta.status()~=5) then
        wifi.sleeptype(0)
        wifi.setmode(1)
        wifi.sta.config(ssid,pass)
        wifi.sta.connect()
    end
    
    local address = "54.86.132.254" -- IP for data.sparkfun.com
    
    tmr.alarm(1,1000,1,function()
    print("connecting")
    if (wifi.sta.status()==5) then
    print("connected")
    sk = net.createConnection(net.TCP, 0)
    sk:on("reconnection",function(conn) print("socket reconnected") end)
    sk:on("disconnection",function(conn) print("socket disconnected") end)
    sk:on("receive", function(conn, msg)
        print(msg)
        local success = nil
        _,_,success = string.find(msg, "success")
        if (success==nil) then
            file.open('unsentData','a+')
            file.writeline(currentDust.P1..","..currentDust.P2)
            file.close()
        end
        wifi.sleeptype(1)
        wifi.sta.disconnect()
        end)
    sk:on("connection",function(conn) print("socket connected")
        print("sending...")
		-- change the name of 05umprticles and 1um_paricles here, or change the GET request for a different server if needed
        conn:send("GET /input/"..PuKey.."?private_key="..PrKey.."&05um_particles="..currentDust.P2.."&1um_particles="..currentDust.P1)
        conn:send(" HTTP/1.1\r\n") 
        conn:send("Host: "..address)
        conn:send("Connection: close\r\n")
        conn:send("Accept: */*\r\n") 
        conn:send("User-Agent: Mozilla/4.0 (compatible; ESP8266;)\r\n") 
        conn:send("\r\n")
    end)
    sk:connect(80, address)
    tmr.stop(1)
    end
    end)
end
