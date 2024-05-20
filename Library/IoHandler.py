import onewire, ds18x20, binascii, ubinascii # type: ignore
import utime as time # type: ignore
from machine import Pin, ADC, PWM, UART, I2C # type: ignore
from Library.ads1x15 import ADS1115
from Library.micropyGPS import MicropyGPS


# Class to handle the IO
class IoHandler:
    # OnBoard Led
    led = Pin("LED", Pin.OUT, value=0)
    # OnBoard Temperature
    temp = ADC(4)
    # Internal Buzzer
    buzzer_in = Pin(18, Pin.OUT, value=0)
    # External Buzzer
    buzzer_out = Pin(22, Pin.OUT, value=0)
    # Panic Switch
    panic = Pin(20, Pin.IN, Pin.PULL_UP)
    # EWT Switch
    ewt = Pin(19, Pin.IN, Pin.PULL_UP)
    # DID / RFID / Temperature
    did = Pin(21)
    # create the onewire object
    ow = onewire.OneWire(did)
    # create the ds18x20 object
    ds = ds18x20.DS18X20(ow)
    # DriverID Initial State
    # Immobilization (az/pt)
    immobilization = PWM(9, freq=1000)
    immobilization.deinit()
    # Start Inhibit (lr)
    start_inhibit = PWM(11, freq=1000)
    start_inhibit.deinit()
    # GPS GT-U7
    uart_0 = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13))
    gps = MicropyGPS(1)
    # CAN SN65HVD230 - 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
    uart_1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    # ADS1015 - A0=ACC - A1=12/24V - A2=Door
    i2c_0 = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)
    adc_0 = ADS1115(i2c_0, address=0x48, gain=0)
    # ADS1015 - A0=Fuel - A1=CANh - A2=CANl
    i2c_1 = I2C(1, scl=Pin(15), sda=Pin(14), freq=100000)
    adc_1 = ADS1115(i2c_1, address=0x48, gain=0)
    # ADC0 - V26 = ADC(26)
    # ADC1 - V27 = ADC(27)
    # ADC2 - Internal Battery
    Vbat = ADC(28)
    # ADC3 - VSYS - Vsys = ADC(29)

    emoji_scanning = '&#128257;'
    emoji_stop = '&#9940;'
    emoji_car = '&#128663;'
    emoji_open = '&#128275;'
    emoji_close = '&#128274;'
    emoji_pressed = '&#128307;'
    emoji_not_pressed = '&#128306;'
    emoji_can_found = '&#128201;'
    emoji_can_lost = '&#128200;'
    emoji_buzzer = '&#128276;'
    emoji_no_buzzer = '&#128277;'
    emoji_first = '&#129351;'
    emoji_second = '&#129352;'
    emoji_third = '&#129353;'
    
    coloured_states = [0, 0, 0, 0]
    
    # Initial State
    dict_lock = {
        'Power': True,
        'Ignition': True,
        'CANh': True,
        'CANl': True,
        'CAN': True,
        'GPS': True,
        'OneWire': True,
        'Temp': True,
        'Fuel': True,
        'Door': True,
        'Panic': True,
        'UDB': True,
        'SI': True,
        'Immo': True,
        'BOut': False,
        'BIn': False}

    dict_data = {
        'Power': emoji_scanning,
        'Ignition': emoji_scanning,
        'CANh': emoji_scanning,
        'CANl': emoji_scanning,
        'CAN': emoji_scanning,
        'GPS': emoji_scanning,
        'OneWire': emoji_scanning,
        'Temp': emoji_scanning,
        'Fuel': emoji_scanning,
        'Door': emoji_scanning,
        'Panic': emoji_scanning,
        'UDB': emoji_scanning}

    dict_info = {
        'Power': 'Scanning',
        'Ignition': 'Scanning',
        'CANh': 'Scanning',
        'CANl': 'Scanning',
        'CAN': 'Scanning',
        'GPS': 'Scanning',
        'OneWire': 'Scanning',
        'Temp': 'Scanning',
        'Fuel': 'Scanning',
        'Door': 'Scanning',
        'Panic': 'Scanning',
        'UDB': 'Scanning',
        'SI': 'Scanning',
        'Immo': 'Scanning',
        'BOut': 'Scanning',
        'BIn': 'Scanning'}

    dict_emoji = {
        'Power': emoji_open,
        'Ignition': emoji_open,
        'CANh': emoji_open,
        'CANl': emoji_open,
        'CAN': emoji_open,
        'GPS': emoji_open,
        'OneWire': emoji_open,
        'Temp': emoji_open,
        'Fuel': emoji_open,
        'Door': emoji_open,
        'Panic': emoji_open,
        'UDB': emoji_open,
        'SI': emoji_open,
        'Immo': emoji_open,
        'BOut': emoji_no_buzzer,
        'BIn': emoji_no_buzzer}


    # Get everything into a starting state
    def __init__(self):
        self.__class__.Get_Power_Reading()
        self.__class__.Get_Ignition_Reading()
        self.__class__.Get_CANh_Reading()
        self.__class__.Get_CANl_Reading()
        self.__class__.Get_CAN_Reading()
        self.__class__.Get_GPS_Reading()
        self.__class__.Get_OneWire_Reading()
        self.__class__.Get_Temp_Reading()
        self.__class__.Get_Fuel_Reading()
        self.__class__.Get_Door_Reading()
        self.__class__.Get_Panic_Reading()
        self.__class__.Get_UDB_Reading()

        self.__class__.show_coloured_leds()
        self.__class__.get_vbat_reading()
        self.__class__.get_pot_reading()
        self.__class__.get_temperature_reading()
        self.__class__.get_time_reading()
                

    # «««««««««««««««««««« G E T »»»»»»»»»»»»»»»»»»»»
    
    @classmethod
    def Get_Power_Reading(cls):
        return cls.dict_data['Power']


    @classmethod
    def Get_Ignition_Reading(cls):
        return cls.dict_data['Ignition']
    

    @classmethod
    def Get_CANh_Reading(cls):
        return cls.dict_data['CANh']


    @classmethod
    def Get_CANl_Reading(cls):
        return cls.dict_data['CANl']
        

    @classmethod
    def Get_CAN_Reading(cls):
        return cls.dict_data['CAN']
    

    @classmethod
    def Get_GPS_Reading(cls):
        return cls.dict_data['GPS']


    @classmethod
    def Get_OneWire_Reading(cls):
        return cls.dict_data['OneWire']


    @classmethod
    def Get_Temp_Reading(cls):
        return cls.dict_data['Temp']


    @classmethod
    def Get_Fuel_Reading(cls):
        return cls.dict_data['Fuel']


    @classmethod
    def Get_Door_Reading(cls):
        return cls.dict_data['Door']


    @classmethod
    def Get_Panic_Reading(cls):
        return cls.dict_data['Panic']
    

    @classmethod
    def Get_UDB_Reading(cls):
        return cls.dict_data['UDB']


    # «««««««««««««««««««« S E T »»»»»»»»»»»»»»»»»»»»
    
    @classmethod
    def Set_Power_Reading(cls):
        if cls.dict_lock['Power']:
            _value = cls.adc_0.read(4, 1)
            _value = cls.convert_voltage(_value)
            cls.dict_data['Power'] = str(round(_value, 2)) + 'V'


    @classmethod
    def Set_Ignition_Reading(cls):
        if cls.dict_lock['Ignition']:
            _value = cls.adc_0.read(4, 0)
            _value = cls.convert_voltage(_value)
            cls.dict_data['Ignition'] = str(round(_value, 2)) + 'V'
    

    @classmethod
    def Set_CANh_Reading(cls):
        if cls.dict_lock['CANh']:
            _value = cls.adc_1.read(4, 1)
            _value = cls.convert_voltage(_value)
            cls.dict_data['CANh'] = str(round(_value, 2)) + 'V'


    @classmethod
    def Set_CANl_Reading(cls):
        if cls.dict_lock['CANl']:
            _value = cls.adc_1.read(4, 2)
            _value = cls.convert_voltage(_value)
            cls.dict_data['CANl'] = str(round(_value, 2)) + 'V'


    @classmethod
    def Set_CAN_Reading(cls):
        if cls.dict_lock['CAN']:
            cls.dict_data['CAN'] = cls.emoji_can_lost
            _value = bytes()
            try:
                _value = cls.uart_1.read(500)
                if _value != None:
                    cls.dict_data['CAN'] = cls.emoji_can_found
                    _value = ubinascii.hexlify(_value, ' ')
                    with open('/Logs/can.txt', 'a') as outfile:
                        outfile.write(cls.get_time_reading() + '\n' + str(_value) + '\r\n')
            except UnicodeError:
                pass


    @classmethod
    def Set_GPS_Reading(cls):
        if cls.dict_lock['GPS']:
            _value = bytes()
            try:
                _value = cls.uart_0.read(500)
                if _value != None:
                    _value = str(_value.decode('utf-8'))
                    _value = _value.splitlines()
                    if len(_value) == 5:
                        for x in range(len(_value)):
                            if _value[x][0:6] == '$GPRMC':
                                _GPRMC = str(_value[x])
                                for y in _GPRMC:
                                    cls.gps.update(y)
                            elif _value[x][0:6] == '$GPVTG':
                                _GPVTG = str(_value[x])
                                for y in _GPVTG:
                                    cls.gps.update(y)
                            elif _value[x][0:6] == '$GPGGA':
                                _GPGGA = str(_value[x])
                                for y in _GPGGA:
                                    cls.gps.update(y)
                            elif _value[x][0:6] == '$GPGSA':
                                _GPGSA = str(_value[x])
                                for y in _GPGSA:
                                    cls.gps.update(y)
                            elif _value[x][0:6] == '$GPGSV':
                                _GPGSV = str(_value[x])
                                for y in _GPGSV:
                                    cls.gps.update(y)
                            elif _value[x][0:6] == '$GPGLL':
                                _GPGLL = str(_value[x])
                                for y in _GPGLL:
                                    cls.gps.update(y)
                            else:
                                if x == 0:
                                    pass
                                else:
                                    with open('/Logs/gps.txt', 'a') as outfile:
                                        outfile.write(cls.get_time_reading() + ' ' + str(x) + '_FAILL -> ' + _value[x] + '\n')
            except UnicodeError:
                pass
        
            if cls.gps.fix_type == 3:
                cls.dict_data['GPS'] = ('3D Fix / ' + str(cls.gps.satellites_in_use) + ' Sat')
                #cls.get_gps_logging()
            elif cls.gps.fix_type == 2:
                cls.dict_data['GPS'] = ('2D Fix / ' + str(cls.gps.satellites_in_use) + ' Sat')
            else:
                cls.dict_data['GPS'] = 'no Fix'


    @classmethod
    def Set_OneWire_Reading(cls):
        if cls.dict_lock['OneWire']:
            ow_info = cls.ow.scan() # OneWire
            ow_list = []
            ds_info = cls.ds.scan() # DS18x20
            ds_list = []
            temp_list = []
            try:
                if ow_info != []:
                    for _ow in range(len(ow_info)):
                        ow_list.append(cls.decode_onewire(ow_info[_ow]))
                if ds_info != []:
                    for _ow in range(len(ds_info)):
                        ds_list.append(cls.decode_onewire(ds_info[_ow]))
                        cls.ds.convert_temp()
                        time.sleep_ms(750) # min of 750ms for OneWire conversion
                        temp_list.append(str(cls.ds.read_temp(ds_info[_ow])))
            except:
                pass
            
            try:
                x = set(ow_list) & set(ds_list)
                if len(x) == 0:
                    cls.dict_data['Temp']= cls.emoji_scanning
                else:
                    cls.dict_data['Temp'] = (str(len(x)) + 'S -> ' + ' / '.join(temp_list))
                    #with open('/Logs/ds18x20.txt', 'a') as outfile:
                    #    outfile.write(cls.get_time_reading() + ' ' + str(ds_list) + ' ' + cls.ds18x20Value + '\n')

                y = set(ow_list) ^ set(ds_list)
                if len(y) == 0:
                    cls.dict_data['OneWire'] = cls.emoji_scanning
                else:
                    cls.dict_data['OneWire'] = ''.join(y)
                    #with open('/Logs/onewire.txt', 'a') as outfile:
                    #    outfile.write(cls.get_time_reading() + ' ' + cls.onewireValue + '\n')
                    cls.buzzer_out_play()
            except:
                pass


    @classmethod
    def decode_onewire(cls, info):
        byte_var = binascii.hexlify(info).decode().upper()
        if len(byte_var) == 16:
            count = 14
            m_list = []
            for _l in range(0, 8, 1):
                ml = byte_var[count:count+2]
                count -= 2
                m_list.append(ml)
            m_list = ''.join(m_list)
            return m_list
        else:
            print('Found OneWire devices with 16 bits error')
            return None


    @classmethod
    def Set_Fuel_Reading(cls):
        if cls.dict_lock['Fuel']:
            _value = cls.adc_1.read(4, 0)
            _value = cls.convert_voltage(_value)
            cls.dict_data['Fuel'] = str(round(_value, 2)) + 'V'
    


    @classmethod
    def Set_Door_Reading(cls):
        if cls.dict_lock['Door']:
            _value = cls.adc_0.read(4, 2)
            _value = cls.convert_voltage(_value)
            cls.dict_data['Door'] = str(round(_value, 2)) + 'V'

    
    @classmethod
    def Set_Panic_Reading(cls):
        if cls.dict_lock['Panic']:
            if cls.panic.value() == 0:
                cls.dict_data['Panic'] = cls.emoji_pressed
                cls.buzzer_out_play()
            else:
                cls.dict_data['Panic'] = cls.emoji_not_pressed
    
        
    @classmethod
    def Set_UDB_Reading(cls):
        if cls.dict_lock['UDB']:
            if cls.ewt.value() == 0:
                cls.dict_data['UDB'] = cls.emoji_pressed
                cls.buzzer_out_play()
            else:
                cls.dict_data['UDB'] = cls.emoji_not_pressed


    # Start Inhibit / Immobilization / Buzzer Out / Buzzer In SET
    @classmethod
    def show_coloured_leds(cls):
        cls.buzzer_out.value(cls.coloured_states[0])
        if cls.coloured_states[1] == 1:
            cls.start_inhibit.duty_u16(500)
        else:
            cls.start_inhibit.deinit()
        if cls.coloured_states[2] == 1:
            cls.immobilization.duty_u16(500)
        else:
            cls.immobilization.deinit()
        cls.buzzer_in.value(cls.coloured_states[3])

    # Start Inhibit / Immobilization / Buzzer Out / Buzzer In SET
    @classmethod
    def set_coloured_leds(cls, states):
        try:
            cls.set_blue_led(states[0])
            cls.set_red_led(states[1])
            cls.set_green_led(states[2])
            cls.set_yellow_led(states[3])
        except:
            pass
        cls.show_coloured_leds()


    # Start Inhibit SET
    @classmethod
    def set_blue_led(cls, state):
        cls.coloured_states[0] = 0 if state == 0 else 1


    # Immobilization SET
    @classmethod
    def set_red_led(cls, state):
        cls.coloured_states[1] = 0 if state == 0 else 1


    # Buzzer Out SET
    @classmethod
    def set_green_led(cls, state):
        cls.coloured_states[2] = 0 if state == 0 else 1


    # Buzzer In SET
    @classmethod
    def set_yellow_led(cls, state):
        cls.coloured_states[3] = 0 if state == 0 else 1


    # Start Inhibit GET
    @classmethod
    def get_blue_led(cls):
        return 0 if cls.coloured_states[0] == 0 else 1


    # Immobilization GET
    @classmethod
    def get_red_led(cls):
        return 0 if cls.coloured_states[1] == 0 else 1


    # Buzzer Out GET
    @classmethod
    def get_green_led(cls):
        return 0 if cls.coloured_states[2] == 0 else 1


    # Buzzer In GET
    @classmethod
    def get_yellow_led(cls):
        return 0 if cls.coloured_states[3] == 0 else 1


    # Visual Vbat
    @classmethod
    def get_pot_reading(cls):
        cls.pot_value = cls.Vbat.read_u16()
        return cls.pot_value
    

    # Vbat
    @classmethod
    def get_vbat_reading(cls):
        cls.pot_value = IoHandler.get_pot_reading()
        cls.vbatValue = (3.3 * (cls.pot_value / 65535)) * 2
        cls.vbatValue = str(round(cls.vbatValue, 2)) + 'V'
        return cls.vbatValue
    

    # Visual temp
    @classmethod
    def get_temp_reading(cls):
        temp_voltage = cls.temp.read_u16() * (3.3 / 65535)
        cls.temp_value = 27 - (temp_voltage - 0.706) / 0.001721
        return cls.temp_value
    
    
    # Sensor de temperatura
    @classmethod
    def get_temperature_reading(cls):
        cls.temp_value = IoHandler.get_temp_reading()
        cls.temperatureValue = str(round(cls.temp_value, 1)) + 'Graus'
        return cls.temperatureValue


    # Local Time Reading
    @classmethod
    def get_time_reading(cls):
        cls.timeValue = cls.get_local_time()
        return cls.timeValue


    

    
    @classmethod
    def convert_voltage(cls, value):
        factor = 6336
        if value <= factor:
            factor = value
        return (24.04 * (value - factor)) / (12336 - factor)


    @classmethod
    def get_local_time(cls):
        utc = 1
        c_time = time.localtime(time.time() + (utc * 3600))
        fmt = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(c_time[0], c_time[1], c_time[2], c_time[3], c_time[4], c_time[5])
        return fmt


    # Buzzer In Play
    @classmethod
    def buzzer_in_play(cls):
        for n in range(3):
            cls.buzzer_in.on()
            time.sleep_ms(50)
            cls.buzzer_in.off()
            time.sleep_ms(50)


    # Buzzer Out Play OneWire
    @classmethod
    def buzzer_out_play(cls):
        for n in range(2):
            cls.buzzer_out.on()
            time.sleep_ms(150)
            cls.buzzer_out.off()
            time.sleep_ms(150)


    @classmethod
    def Set_Switches_Reading(cls, value):
        status = 'OK'
        if value == 'Power':
            cls.dict_lock['Power'] = not cls.dict_lock['Power']
            if cls.dict_lock['Power']:
                cls.dict_emoji['Power'] = cls.emoji_open
            else:
                cls.dict_emoji['Power'] = cls.emoji_close
        elif value == 'Ignition':
            cls.dict_lock['Ignition'] = not cls.dict_lock['Ignition']
            if cls.dict_lock['Ignition']:
                cls.dict_emoji['Ignition'] = cls.emoji_open
            else:
                cls.dict_emoji['Ignition'] = cls.emoji_close
        elif value == 'CANh':
            cls.dict_lock['CANh'] = not cls.dict_lock['CANh']
            if cls.dict_lock['CANh']:
                cls.dict_emoji['CANh'] = cls.emoji_open
            else:
                cls.dict_emoji['CANh'] = cls.emoji_close
        elif value == 'CANl':
            cls.dict_lock['CANl'] = not cls.dict_lock['CANl']
            if cls.dict_lock['CANl']:
                cls.dict_emoji['CANl'] = cls.emoji_open
            else:
                cls.dict_emoji['CANl'] = cls.emoji_close
        elif value == 'CAN':
            cls.dict_lock['CAN'] = not cls.dict_lock['CAN']
            if cls.dict_lock['CAN']:
                cls.dict_emoji['CAN'] = cls.emoji_open
            else:
                cls.dict_emoji['CAN'] = cls.emoji_close
        elif value == 'GPS':
            cls.dict_lock['GPS'] = not cls.dict_lock['GPS']
            if cls.dict_lock['GPS']:
                cls.dict_emoji['GPS'] = cls.emoji_open
            else:
                cls.dict_emoji['GPS'] = cls.emoji_close
        elif value == 'OneWire':
            cls.dict_lock['OneWire'] = not cls.dict_lock['OneWire']
            if cls.dict_lock['OneWire']:
                cls.dict_emoji['OneWire'] = cls.emoji_open
            else:
                cls.dict_emoji['OneWire'] = cls.emoji_close
        elif value == 'Temp':
            cls.dict_lock['Temp'] = not cls.dict_lock['Temp']
            if cls.dict_lock['Temp']:
                cls.dict_emoji['Temp'] = cls.emoji_open
            else:
                cls.dict_emoji['Temp'] = cls.emoji_close
        elif value == 'Fuel':
            cls.dict_lock['Fuel'] = not cls.dict_lock['Fuel']
            if cls.dict_lock['Fuel']:
                cls.dict_emoji['Fuel'] = cls.emoji_open
            else:
                cls.dict_emoji['Fuel'] = cls.emoji_close
        elif value == 'Door':
            cls.dict_lock['Door'] = not cls.dict_lock['Door']
            if cls.dict_lock['Door']:
                cls.dict_emoji['Door'] = cls.emoji_open
            else:
                cls.dict_emoji['Door'] = cls.emoji_close
        elif value == 'Panic':
            cls.dict_lock['Panic'] = not cls.dict_lock['Panic']
            if cls.dict_lock['Panic']:
                cls.dict_emoji['Panic'] = cls.emoji_open
            else:
                cls.dict_emoji['Panic'] = cls.emoji_close
        elif value == 'UDB':
            cls.dict_lock['UDB'] = not cls.dict_lock['UDB']
            if cls.dict_lock['UDB']:
                cls.dict_emoji['UDB'] = cls.emoji_open
            else:
                cls.dict_emoji['UDB'] = cls.emoji_close
        elif value == 'SI':
            cls.dict_lock['SI'] = not cls.dict_lock['SI']
            if cls.dict_lock['SI']:
                cls.dict_emoji['SI'] = cls.emoji_open
            else:
                cls.dict_emoji['SI'] = cls.emoji_close
        elif value == 'Immo':
            cls.dict_lock['Immo'] = not cls.dict_lock['Immo']
            if cls.dict_lock['Immo']:
                cls.dict_emoji['Immo'] = cls.emoji_open
            else:
                cls.dict_emoji['Immo'] = cls.emoji_close
        elif value == 'BOut':
            cls.dict_lock['BOut'] = not cls.dict_lock['BOut']
            if cls.dict_lock['BOut']:
                cls.dict_emoji['BOut'] = cls.emoji_buzzer
            else:
                cls.dict_emoji['BOut'] = cls.emoji_no_buzzer
        elif value == 'BIn':
            cls.dict_lock['BIn'] = not cls.dict_lock['BIn']
            if cls.dict_lock['BIn']:
                cls.dict_emoji['BIn'] = cls.emoji_buzzer
            else:
                cls.dict_emoji['BIn'] = cls.emoji_no_buzzer
        elif value == 'Reboot':
            raise RuntimeError
        elif value == 'POff':
            raise KeyboardInterrupt
        else:
            status = 'Error'
        return status




    # GPS Logging
    @classmethod
    def get_gps_logging(cls):
        cls.gps.start_logging('/Logs/gps_logging.txt')
        cls.gps.write_log('Latitude      : ' + str(cls.gps.latitude_string()) + '\r\n')
        cls.gps.write_log('Longitude     : ' + str(cls.gps.longitude_string()) + '\r\n')
        cls.gps.write_log('Altitude      : ' + str(cls.gps.altitude) + '\r\n')
        cls.gps.write_log('Km/h          : ' + str(cls.gps.speed_string('kph')) + '\r\n')
        cls.gps.write_log('Compass       : ' + str(cls.gps.compass_direction()) + '\r\n')
        cls.gps.write_log('Date1         : ' + str(cls.gps.date_string('long')) + '\r\n')
        cls.gps.write_log('Date2         : ' + str(cls.gps.date_string('s_dmy')) + '\r\n')
        cls.gps.write_log('Time Since Fix: ' + str(cls.gps.time_since_fix()) + '\r\n')
        cls.gps.write_log('No Satellites : ' + str(cls.gps.satellites_in_use) + '\r\n')
        cls.gps.write_log('Satellites    : ' + str(cls.gps.satellites_used) + '\r\n')
        cls.gps.write_log('Fix type      : ' + str(cls.gps.fix_type) + '\r\n')
        cls.gps.write_log('\r\n')
        cls.gps.stop_logging()
