import onewire, ds18x20, binascii, ubinascii
import utime as time
from machine import Pin, ADC, PWM, UART, I2C
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

    # Initial State
    coloured_states = [0, 0, 0, 0]
    Initial_State = 'Scanning'
    lockOpen = '&#128275;'
    lockClose = '&#128274;'
    
    vrValue = Initial_State
    amValue = Initial_State
    canhValue = Initial_State
    canlValue = Initial_State
    canValue = Initial_State 
    gpsValue = Initial_State 
    onewireValue = Initial_State
    ds18x20Value = Initial_State
    brValue = Initial_State
    ctValue = Initial_State
    azValue = Initial_State
    rsValue = Initial_State
    
    vr_stat =      True
    am_stat =      False
    canh_stat =    False
    canl_stat =    False
    can_stat =     False
    gps_stat =     False
    onewire_stat = False
    ds18x20_stat = False
    br_stat =      False
    ct_stat =      False
    az_stat =      False
    rs_stat =      False

    vr_st =      lockOpen
    am_st =      lockClose
    canh_st =    lockClose
    canl_st =    lockClose
    can_st =     lockClose
    gps_st =     lockClose
    onewire_st = lockClose
    ds18x20_st = lockClose
    br_st =      lockClose
    ct_st =      lockClose
    az_st =      lockClose
    rs_st =      lockClose


    # Get everything into a starting state
    def __init__(self):
        # Voltage Sensors
        self.__class__.get_vr_reading()
        self.__class__.get_am_reading()
        self.__class__.get_canh_reading()
        self.__class__.get_canl_reading()
        self.__class__.get_br_reading()
        self.__class__.get_ct_reading()
        # Botões, Relés, Buzzer
        self.__class__.get_az_reading()
        self.__class__.get_rs_reading()
        self.__class__.show_coloured_leds()
        # CAN, GPS, DriverID
        self.__class__.get_can_reading()
        self.__class__.get_gps_reading()
        self.__class__.get_onewire_reading()
        self.__class__.get_ds18x20_reading()
        # Sensores internos
        self.__class__.get_vbat_reading()
        self.__class__.get_pot_reading()
        self.__class__.get_temperature_reading()
        self.__class__.get_time_reading()
                

    # Power GET
    @classmethod
    def get_vr_reading(cls):
        return cls.vrValue


    # Power SET
    @classmethod
    def set_vr_reading(cls):
        if cls.vr_stat:
            _vr_Value = cls.adc_0.read(4, 1)
            _vr_Value = cls.convert_voltage(_vr_Value)
            cls.vrValue = str(round(_vr_Value, 2)) + 'V'
            return cls.vrValue


    # Ignition GET
    @classmethod
    def get_am_reading(cls):
        return cls.amValue
    

    # Ignition SET
    @classmethod
    def set_am_reading(cls):
        if cls.am_stat:
            _am_Value = cls.adc_0.read(4, 0)
            _am_Value = cls.convert_voltage(_am_Value)
            cls.amValue = str(round(_am_Value, 2)) + 'V'
            return cls.amValue


    # CAN h GET
    @classmethod
    def get_canh_reading(cls):
        return cls.canhValue
    

    # CAN h SET
    @classmethod
    def set_canh_reading(cls):
        if cls.canh_stat:
            _canh_Value = cls.adc_1.read(4, 1)
            _canh_Value = cls.convert_voltage(_canh_Value)
            cls.canhValue = str(round(_canh_Value, 2)) + 'V'
            return cls.canhValue


    # CAN l GET
    @classmethod
    def get_canl_reading(cls):
        return cls.canlValue
    

    # CAN l SET
    @classmethod
    def set_canl_reading(cls):
        if cls.canl_stat:
            _canl_Value = cls.adc_1.read(4, 2)
            _canl_Value = cls.convert_voltage(_canl_Value)
            cls.canlValue = str(round(_canl_Value, 2)) + 'V'
            return cls.canlValue


    # CanBus GET
    @classmethod
    def get_can_reading(cls):
        return cls.canValue
    

    # CanBus SET
    @classmethod
    def set_can_reading(cls):
        if cls.can_stat:
            cls.canValue = 'Can Lost'
            _rxData = bytes()
            try:
                _rxData = cls.uart_1.read(500)
                if _rxData != None:
                    cls.canValue = 'Can Found'
                    _rxData = ubinascii.hexlify(_rxData, ' ')
                    with open('/Logs/can.txt', 'a') as outfile:
                        outfile.write(cls.get_time_reading() + '\n' + str(_rxData) + '\r\n')
            except UnicodeError:
                pass
    

    # GPS GET
    @classmethod
    def get_gps_reading(cls):
        return cls.gpsValue


    # GPS SET
    @classmethod
    def set_gps_reading(cls):
        if cls.gps_stat: 
            _rxData = bytes()
            try:
                _rxData = cls.uart_0.read(500)
                if _rxData != None:
                    _rxData = str(_rxData.decode('utf-8'))
                    _rxData = _rxData.splitlines()
                    if len(_rxData) == 5:
                        for x in range(len(_rxData)):
                            if _rxData[x][0:6] == '$GPRMC':
                                _GPRMC = str(_rxData[x])
                                for y in _GPRMC:
                                    cls.gps.update(y)
                            elif _rxData[x][0:6] == '$GPVTG':
                                _GPVTG = str(_rxData[x])
                                for y in _GPVTG:
                                    cls.gps.update(y)
                            elif _rxData[x][0:6] == '$GPGGA':
                                _GPGGA = str(_rxData[x])
                                for y in _GPGGA:
                                    cls.gps.update(y)
                            elif _rxData[x][0:6] == '$GPGSA':
                                _GPGSA = str(_rxData[x])
                                for y in _GPGSA:
                                    cls.gps.update(y)
                            elif _rxData[x][0:6] == '$GPGSV':
                                _GPGSV = str(_rxData[x])
                                for y in _GPGSV:
                                    cls.gps.update(y)
                            elif _rxData[x][0:6] == '$GPGLL':
                                _GPGLL = str(_rxData[x])
                                for y in _GPGLL:
                                    cls.gps.update(y)
                            else:
                                if x == 0:
                                    pass
                                else:
                                    with open('/Logs/gps.txt', 'a') as outfile:
                                        outfile.write(cls.get_time_reading() + ' ' + str(x) + '_FAILL -> ' + _rxData[x] + '\n')
            except UnicodeError:
                pass
        
            if cls.gps.fix_type == 3:
                cls.gpsValue = ('3D Fix / ' + str(cls.gps.satellites_in_use) + ' Sat')
                #cls.get_gps_logging()
            elif cls.gps.fix_type == 2:
                cls.gpsValue = ('2D Fix / ' + str(cls.gps.satellites_in_use) + ' Sat')
            else:
                cls.gpsValue = 'no Fix'


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


    # OneWire GET
    @classmethod
    def get_onewire_reading(cls):
        return cls.onewireValue
        

    # DS18x20 GET
    @classmethod
    def get_ds18x20_reading(cls):
        return cls.ds18x20Value


    # OneWire / DS18x20 SET
    @classmethod
    def set_onewire_reading(cls):
        if cls.onewire_stat: 
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
                    cls.ds18x20Value = cls.Initial_State
                else:
                    cls.ds18x20Value = (str(len(x)) + 'S -> ' + ' / '.join(temp_list))
                    #with open('/Logs/ds18x20.txt', 'a') as outfile:
                    #    outfile.write(cls.get_time_reading() + ' ' + str(ds_list) + ' ' + cls.ds18x20Value + '\n')

                y = set(ow_list) ^ set(ds_list)
                if len(y) == 0:
                    cls.onewireValue = cls.Initial_State
                else:
                    cls.onewireValue = ''.join(y)
                    with open('/Logs/onewire.txt', 'a') as outfile:
                        outfile.write(cls.get_time_reading() + ' ' + cls.onewireValue + '\n')
                    cls.buzzer_out_play()
            except:
                pass


    # Decode OneWire FUNCTION
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

    
    # Fuel Level GET
    @classmethod
    def get_br_reading(cls):
        return cls.brValue


    # Fuel Level SET
    @classmethod
    def set_br_reading(cls):
        if cls.br_stat: 
            _br_Value = cls.adc_1.read(4, 0)
            _br_Value = cls.convert_voltage(_br_Value)
            cls.brValue = str(round(_br_Value, 2)) + 'V'
            return cls.brValue


    # Door Sensor GET
    @classmethod
    def get_ct_reading(cls):
        return cls.ctValue


    # Door Sensor SET
    @classmethod
    def set_ct_reading(cls):
        if cls.ct_stat: 
            _ct_Value = cls.adc_0.read(4, 2)
            _ct_Value = cls.convert_voltage(_ct_Value)
            cls.ctValue = str(round(_ct_Value, 2)) + 'V'
            return cls.ctValue


    # Panic Button GET
    @classmethod
    def get_az_reading(cls):
        return cls.azValue

    
    # Panic Button SET
    @classmethod
    def set_az_reading(cls):
        if cls.az_stat: 
            if cls.panic.value() == 0:
                cls.azValue = 'Pressed'
                cls.buzzer_out_play()
            else:
                cls.azValue = cls.Initial_State
            return cls.azValue
    
    
    # Unauthorized Driver Button GET
    @classmethod
    def get_rs_reading(cls):
        return cls.rsValue
    

    # Unauthorized Driver Button SET
    @classmethod
    def set_rs_reading(cls):
        if cls.rs_stat: 
            if cls.ewt.value() == 0:
                cls.rsValue = 'Pressed'
                cls.buzzer_out_play()
            else:
                cls.rsValue = cls.Initial_State
            return cls.rsValue


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


    # Lock Status
    @classmethod
    def lock_status(cls, state):
        print(state)
        """
        if state[0] == 1:
            cls.vr_stat = not cls.vr_stat
            if cls.vr_stat:
                cls.vr_st = '-1-'
            else:
                cls.vr_st = '-0-'
        """
