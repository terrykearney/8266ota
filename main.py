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
