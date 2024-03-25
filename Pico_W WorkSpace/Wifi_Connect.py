import network
from rp2 import country
from ubinascii import hexlify
from encode import encode, to_csv
from decode import decode, from_csv
from Board_Led import led_on, led_blink, led_off


def salt():
    return "fzdF7T8sKHAtXPahVge3bJ"


def en_code():
    '''
    Encode
    '''
    to_csv('wifi_username.dat',encode('username', salt()))
    to_csv('wifi_password.dat',encode('password', salt()))


def de_code():
    '''
    Decode
    '''
    ssid = decode(from_csv('wifi_username.dat'), salt())
    password = decode(from_csv('wifi_password.dat'), salt())
    return ssid, password


def network_activate():
    '''
    Set WiFi to station interface
    Activate the network interface
    '''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Power-Saving mode - Disabled
    wlan.config(pm = 0xa11140)
    # Change Country
    country('PT')
    ssid, password = de_code()
    wlan.connect(ssid, password)
    network_waiting(wlan)
    network_status(wlan)
    return wlan


def network_waiting(wlan):
    '''
    Waiting for connection
    '''
    max_wait = 10
    while max_wait > 0:
        max_wait -= 1
        if wlan.status() < 0 or wlan.status() >= 3:
            # Connection Successful
            status = cyw43_status(wlan)
            print(str(max_wait) + ' Waiting for connection... ' + status)
            break
        status = cyw43_status(wlan)
        print(str(max_wait) + ' Waiting for connection... ' + status)
        led_blink()


def network_status(wlan):
    '''
    Check Connection
    
    '''
    if wlan.status() != 3:
        # No connection
        network_disconnect(wlan)
        raise RuntimeError('Network connection failed')
    else:
        # Info Connection
        led_on()
        # IP
        print('IP:', wlan.ifconfig()[0])
        # MAC Address
        print('MAC:', hexlify(network.WLAN().config('mac'),':').decode())
        # Country
        print('Country:', country())
        # Other things you can query
        print('Channel:', wlan.config('channel'))
        print('SSID:', wlan.config('essid'))
        print('TX Power:', wlan.config('txpower'))


def cyw43_status(wlan):
    '''
    Return value of cyw43_wifi_link_status
    
       -3  STAT_WRONG_PASSWORD  -- failed due to incorrect password
       -2  STAT_NO_AP_FOUND     -- failed because no access point replied
       -1  STAT_CONNECT_FAIL    -- failed due to other problems
        0  STAT_IDLE            -- no connection and no activity
        1  STAT_CONNECTING      -- connecting in progress
        2  STAT_NO_IP           -- connecting no ip
        3  STAT_GOT_IP          -- connection successful
    '''
    if wlan.status() == 0:
        return 'LINK_DOWN -- no connection and no activity'
    if wlan.status() == 1:
        return 'LINK_JOIN -- connecting in progress'
    if wlan.status() == 2:
        return 'LINK_NO_IP -- connecting no ip'
    if wlan.status() == 3:
        return 'LINK_UP -- connection successful'
    if wlan.status() == -1:
        return 'LINK_FAIL -- failed due to other problems'
    if wlan.status() == -2:
        return 'LINK_NO_NET -- failed because no access point replied'
    if wlan.status() == -3:
        return 'LINK_BAD_AUTH -- failed due to incorrect password'


def network_disconnect(wlan):
    '''
    Disconnect network
    '''
    led_off()
    wlan.disconnect()
    print('Disconnected')
