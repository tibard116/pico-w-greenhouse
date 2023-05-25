from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from machine import ADC, Pin
from time import sleep
import utime
import dht
import machine
import network
import socket


WIDTH = 128
HEIGHT =  32

# Initialize I2C bus and OLED display
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)  # use 0x3C as the display I2C address

# Initialize DHT22 sensor
d = dht.DHT22(Pin(2))

# Initialize the analog pin for the YL-69 sensor
soil = ADC(Pin(26))  # GPIO26 also its plug into 3.3v

# Read the value from the sensor
readDelay = 1

#Calibraton values
min_moisture= 14000
max_moisture= 65000



# Clear the display
oled.fill(0)

# Read temperature and humidity values from the sensor
d.measure()
temp = d.temperature()
humidity = d.humidity()
moisture = round(max_moisture-soil.read_u16())*100/(max_moisture-min_moisture)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("ssid","password")



def web_page():
    bme = d          #BME280 object created
    html = """<html><head><meta http-equiv="refresh" content="5"><meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"><style>body { text-align: center; font-family: "Helvetica", Arial;}
  table { border-collapse: collapse; width:55%; margin-left:auto; margin-right:auto; }
  th { padding: 12px; background-color: #87034F; color: white; }
  tr { border: 2px solid #000556; padding: 12px; }
  tr:hover { background-color: #bcbcbc; }
  td { border: none; padding: 14px; }
  .sensor { color:DarkBlue; font-weight: bold; background-color: #ffffff; padding: 1px;  
  </style></head><body><h1>Rick Green House Monitor</h1>
  <table><tr><th>Parameters</th><th>Value</th></tr>
  <tr><td>Temperature C</td><td><span class="sensor">""" + str(temp) + " C" + """</span></td></tr>
  <tr><td>Humidity %</td><td><span class="sensor">""" + str("%.2f%%" % humidity)  + """</span></td></tr> 
  <tr><td>Soil Moisture %</td><td><span class="sensor">""" + str("%.2f%%" % moisture) + """</span></td></tr>
  
  <head><meta http-equiv="refresh" content="5"><meta name="viewport" content="width=device-width, initial-scale=1"><style>img{display: block; margin-left: auto; margin-right: auto;}</style></head><body><img src="data:image/jpeg;base64,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" alt="pico" style="max-width:100%;">
  </body></html>"""
    return html
  
# Wait for connect or fail
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)

    
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 80))
server.listen(5)
print('listening on', addr)

# Write the values to the display

    
while True:
       
    
    print("moisture: " + "%.2f" % moisture +"% (adc: "+str(soil.read_u16())+")")
    utime.sleep(readDelay)
    oled.text("TEMP: {} C".format(temp), 0, 0)
    oled.text("Humidity: {} %".format(humidity), 0, 10)
    oled.text("soil: {} ".format(moisture), 0, 20)
    oled.text("Wifi: {} ".format(ip), 0, 30)
    oled.show()



    try:
        conn, addr = server.accept()
        conn.settimeout(3.0)
        print('client connected from', addr)
        request = conn.recv(1024)
        conn.settimeout(None)
        # HTTP-Request receive
        print('Request:', request)              
        # HTTP-Response send
        response = web_page()
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.sendall(response)
        conn.close()
        

        

    
    except OSError as e:
        conn.close()
        print('connection closed')
        

        
        
   
        
        

    