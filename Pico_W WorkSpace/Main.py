from Wifi_Connect import network_activate, network_disconnect
import Get_Time


wlan = network_activate()
date, time = view_time()
network_disconnect(wlan)
