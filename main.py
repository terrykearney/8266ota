import machine
import dht
import time
from machine import Pin, ADC
import network
import espnow

from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

firmware_url = "https://github.com/terrykearney/8266ota/main/"

ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "test.py")
ota_updater.download_and_install_update_if_available()

# === SAFETY DELAY - PREVENTS LOCKUP ===
print("="*40)
print("Starting in 3 seconds...")
print("Press Ctrl+C NOW to stop!")
print("="*40)
time.sleep(3)
voltage = 0  # Initialize global variable
temp = 0
hum = 0

def battery():
    global voltage
    # Voltage divider resistors
    R1 = 30000  # 30kΩ
    R2 = 7500   # 7.5kΩ
    
    try:
        adc = machine.ADC(0)
        
        print("Reading ADC values from ESP8266-12F")
        print("ADC Range: 0-1024 (0-1.0V)")
        print("-" * 40)
        
        # Read raw ADC value (0-1024)
        raw_value = adc.read()
        
        # Convert to voltage (ESP8266 ADC measures 0-1.0V)
        voltage = (raw_value / 1024.0) * 0.985
        
        # Calculate actual battery voltage (before divider)
        voltage = voltage * (R1 + R2) / R2
        print(f"ADC Value: {raw_value:4d} | Voltage: {voltage:.3f}V")
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Battery reading error: {e}")
        voltage = 0

def timestamp_to_datetime(ts):
    try:
        dt = time.localtime(ts)
        date = "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])
        time_str = "{:02d}:{:02d}:{:02d}".format(dt[3], dt[4], dt[5])
        return date, time_str
    except Exception as e:
        print(f"Timestamp error: {e}")
        return "0000-00-00", "00:00:00"

# Get timestamp and format
timestamp = time.time()
date_str, time_str = timestamp_to_datetime(timestamp)

# Initialize battery reading
battery()

# Initialize ESP-NOW
try:
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    esp = espnow.ESPNow()
    esp.active(True)
    
    # Add peer
    peer1 = b'\x98=\xae\xb4LD'
    esp.add_peer(peer1)
    espnow_ready = True
    print("ESP-NOW initialized successfully")
except Exception as e:
    print(f"ESP-NOW initialization error: {e}")
    espnow_ready = False

# Initialize DHT22 sensor
try:
    sensor = dht.DHT22(machine.Pin(2))
    print("DHT22 sensor initialized")
except Exception as e:
    print(f"DHT22 initialization error: {e}")
    sensor = None

# Read sensor data
if sensor:
    try:
        # Measure
        sensor.measure()
        
        # Get readings
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        # Print results
        print(f"Temperature: {temp:.1f}°C")
        print(f"Humidity: {hum:.1f}%")
        
    except OSError as e:
        print(f"Failed to read sensor: {e}")
        temp = 0
        hum = 0
    except Exception as e:
        print(f"Unexpected sensor error: {e}")
        temp = 0
        hum = 0
else:
    print("Sensor not available, using default values")
    temp = 0
    hum = 0

# Wait 2 seconds between readings
time.sleep(2)

t1 = temp
h1 = hum

# Get battery voltage again
battery()
print(f"Battery Voltage: {voltage}V")

# Create message
message = str(t1) + " " + str(h1) + " " + str(time_str) + " " + str(voltage)

print(f"Temperature: {t1}°C, Humidity: {h1}%")
print(f"Sending Data: {message}")

# Send via ESP-NOW
if espnow_ready:
    try:
        esp.send(peer1, message)
        print("Data sent successfully")
    except Exception as e:
        print(f"Failed to send data: {e}")
else:
    print("ESP-NOW not available, skipping send")
print("Test")
time.sleep(10)

# Enter deep sleep for 15 mins (900000 milliseconds)
print("Entering deep sleep for 30 mins...")
machine.deepsleep(180000)  # 15 mins = 900000

