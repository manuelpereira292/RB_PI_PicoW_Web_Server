from Library.NetworkCredentials import NetworkCredentials
from rp2 import country # type: ignore
import utime as time # type: ignore
import ntptime, network # type: ignore


# class to handle WiFi conenction
class WiFiConnection:
    # class level vars accessible to all code
    status = network.STAT_IDLE
    ip = ""
    subnet_mask = ""
    gateway = ""
    dns_server = ""
    wlan = None

    def __init__(self):
        pass

    @classmethod
    def start_station_mode(cls, print_progress=False):
        # set WiFi to station interface
        cls.wlan = network.WLAN(network.STA_IF)
        # activate the network interface
        cls.wlan.active(True)
        # Power-Saving mode - Disabled
        cls.wlan.config(pm = 0xa11140)
        # Change Country
        country('PT')
        # connect to wifi network
        ssid = NetworkCredentials.ssid2
        password = NetworkCredentials.password2
        cls.wlan.connect(ssid, password)
        cls.status = network.STAT_CONNECTING
        if print_progress:
            print("Connecting to Wi-Fi - Please Wait...")
        max_wait = 20
        # wait for connection - poll every 0.5 secs
        while max_wait > 0:
            """
                0   STAT_IDLE           -- no connection and no activity,
                1   STAT_CONNECTING     -- connecting in progress,
               -3   STAT_WRONG_PASSWORD -- failed due to incorrect password,
               -2   STAT_NO_AP_FOUND    -- failed because no access point replied,
               -1   STAT_CONNECT_FAIL   -- failed due to other problems,
                3   STAT_GOT_IP         -- connection successful.
            """
            if cls.wlan.status() < 0 or cls.wlan.status() >= 3:
                # connection attempt finished
                break
            max_wait -= 1
            time.sleep(0.5)

        # check connection
        cls.status = cls.wlan.status()
        if cls.wlan.status() != 3:
            # No connection
            if print_progress:
                print("Connection Failed")
            return False
        else:
            # connection successful
            config = cls.wlan.ifconfig()
            cls.ip = config[0]
            cls.subnet_mask = config[1]
            cls.gateway = config[2]
            cls.dns_server = config[3]
            if print_progress:
                print('IP = ' + str(cls.ip))
            # Ajustar Data/Hora através da rede
            ntptime.host = "1.europe.pool.ntp.org"
            for _n in range (10):
                try:
                    ntptime.settime()
                except OSError as error:
                    print('Error Set Local Time: ', error)
                if time.localtime()[0] == 2024:
                    break
            return True
