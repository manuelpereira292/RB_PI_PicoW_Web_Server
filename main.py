# Using asyncio for non blocking web server
from Library.WiFiConnection import WiFiConnection
from Library.RequestParser import RequestParser
from Library.ResponseBuilder import ResponseBuilder
from Library.IoHandler import IoHandler
import machine, uasyncio, sys # type: ignore


# Connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('Network connection failed...')


# Coroutine to handle HTTP request
async def handle_request(reader, writer):
    try:
        # Allow other tasks to run while waiting for data
        raw_request = await reader.read(2048) # TEST 2048 - 4096
        request = RequestParser(raw_request)
        response_builder = ResponseBuilder()
        # Filter out api request
        if request.url_match("/api"):
            action = request.get_action()
            if action == 'readData':
                # Ajax request for data
                # Sensores voltagens
                vrValue = IoHandler.get_vr_reading()
                amValue = IoHandler.get_am_reading()
                canhValue = IoHandler.get_canh_reading()
                canlValue = IoHandler.get_canl_reading()
                brValue = IoHandler.get_br_reading()
                ctValue = IoHandler.get_ct_reading()
                # Botões, Relés, Buzzer
                azValue = IoHandler.get_az_reading()
                rsValue = IoHandler.get_rs_reading()
                # CAN, GPS, DriverID
                canValue = IoHandler.get_can_reading()
                gpsValue = IoHandler.get_gps_reading()
                onewireValue = IoHandler.get_onewire_reading()
                ds18x20Value = IoHandler.get_ds18x20_reading()
                # Sensores internos
                vbatValue = IoHandler.get_vbat_reading()
                pot_value = IoHandler.get_pot_reading()
                temperatureValue = IoHandler.get_temperature_reading()
                timeValue = IoHandler.get_time_reading()
                temp_value = IoHandler.get_temp_reading()

                cled_states = {
                    'blue': IoHandler.get_blue_led(),
                    'red': IoHandler.get_red_led(),
                    'green': IoHandler.get_green_led(),
                    'yellow': IoHandler.get_yellow_led()}
                
                lockClose = '&#128274;'

                response_obj = {
                    'status': 0,
                    'vrValue': vrValue,
                    'amValue': amValue,
                    'canhValue': canhValue,
                    'canlValue': canlValue,
                    'brValue': brValue,
                    'ctValue': ctValue,
                    'azValue': azValue,
                    'rsValue': rsValue,
                    'cled_states': cled_states,
                    'canValue': canValue,
                    'gpsValue': gpsValue,
                    'onewireValue': onewireValue,
                    'ds18x20Value': ds18x20Value,
                    'vbatValue': vbatValue,
                    'pot_value': pot_value,
                    'temperatureValue': temperatureValue,
                    'timeValue': timeValue,
                    'temp_value': temp_value,
                    
                    'vr_st':      lockClose,
                    'am_st':      lockClose,
                    'canh_st':    lockClose,
                    'canl_st':    lockClose,
                    'can_st':     lockClose,
                    'gps_st':     lockClose,
                    'onewire_st': lockClose,
                    'ds18x20_st': lockClose,
                    'br_st':      lockClose,
                    'ct_st':      lockClose,
                    'az_st':      lockClose,
                    'rs_st':      lockClose,
                    }
                
                response_builder.set_body_from_dict(response_obj)
            
            # Rotina Interruptores
            elif action == 'setLedColour':
                # turn on requested coloured led
                status = 'OK'
                # returns json object with led states
                led_colour = request.data()['colour']
                
                print(led_colour)
                cled_states = {
                    'blue': 0,
                    'red': 0,
                    'green': 0,
                    'yellow': 0}

                lock_states = {
                    'Power': 0,
                    'Ignition': 0,
                    'CANH': 0,
                    'CANL': 0,
                    'CAN': 0,
                    'GPS': 0,
                    'OneWire': 0,
                    'DS18x20': 0,
                    'Fuel': 0,
                    'Door': 0,
                    'Panic': 0,
                    'UDB': 0}

                if led_colour == 'blue':
                    cled_states['blue'] = 1
                elif led_colour == 'red':
                    cled_states['red'] = 1
                elif led_colour == 'green':
                    cled_states['green'] = 1
                elif led_colour == 'yellow':
                    cled_states['yellow'] = 1
                elif led_colour == 'off':
                    pass # leave leds off
                
                elif led_colour == 'Power':
                    lock_states['Power'] = 1
                elif led_colour == 'Ignition':
                    lock_states['Ignition'] = 1
                elif led_colour == 'CANH':
                    lock_states['CANH'] = 1
                elif led_colour == 'CANL':
                    lock_states['CANL'] = 1
                elif led_colour == 'CAN':
                    lock_states['CAN'] = 1
                elif led_colour == 'GPS':
                    lock_states['GPS'] = 1
                elif led_colour == 'OneWire':
                    lock_states['OneWire'] = 1
                elif led_colour == 'DS18x20':
                    lock_states['DS18x20'] = 1
                elif led_colour == 'Fuel':
                    lock_states['Fuel'] = 1
                elif led_colour == 'Door':
                    lock_states['Door'] = 1
                elif led_colour == 'Panic':
                    lock_states['Panic'] = 1
                elif led_colour == 'UDB':
                    lock_states['UDB'] = 1
                else:
                    status = 'Error'

                IoHandler.set_coloured_leds([
                    cled_states['blue'],
                    cled_states['red'],
                    cled_states['green'],
                    cled_states['yellow']])
                
                IoHandler.lock_status([
                    lock_states['Power'],
                    lock_states['Ignition'],
                    lock_states['CANH'],
                    lock_states['CANL'],
                    lock_states['CAN'],
                    lock_states['GPS'],
                    lock_states['OneWire'],
                    lock_states['DS18x20'],
                    lock_states['Fuel'],
                    lock_states['Door'],
                    lock_states['Panic'],
                    lock_states['UDB']])

                response_obj = {
                    'status': status,
                    'cled_states': cled_states}
                
                response_builder.set_body_from_dict(response_obj)
            
            # Rotina de Reiniciar e Desligar
            elif action == 'setRgbColour':
                try:
                    rgb_color = request.data()['color']
                except:
                    rgb_color = None

                if rgb_color == 'reiniciar':
                    IoHandler.buzzer_in_play()
                    IoHandler.led.off()
                    machine.reset()
                elif rgb_color == 'desligar':
                    IoHandler.buzzer_in_play()
                    IoHandler.led.off()
                    sys.exit()
                elif rgb_color == None:
                    pass

            else:
                # unknown action
                response_builder.set_status(404)

        # try to serve static file
        else:
            response_builder.serve_static_file(request.url, "/Assets/HTML/api_index.html")

        # build response message
        response_builder.build_response()
        # send reponse back to client
        writer.write(response_builder.response)
        # allow other tasks to run while data being sent
        await writer.drain()
        await writer.wait_closed()
    
    except OSError as _e1:
        print('OSError: ', _e1)
    except UnicodeError as _e2:
        print('UnicodeError: ', _e2)
    except MemoryError as _e3:
        print('MemoryError: ', _e3)
    except:
        print('Error: ???')


# coroutine that will run as the neopixel update task
async def neopixels():

    counter = 0
    while True:
        if counter % 1000 == 0:
            IoHandler.set_vr_reading()
            IoHandler.set_am_reading()
            IoHandler.set_canh_reading()
            IoHandler.set_canl_reading()
            IoHandler.set_br_reading()
            IoHandler.set_ct_reading()
            IoHandler.set_az_reading()
            IoHandler.set_rs_reading()

        counter += 1
        # 0 second pause to allow other tasks to run
        await uasyncio.sleep(0)


# main coroutine to boot async tasks
async def main():
    # start web server task
    print('Setting up webserver...')
    server = uasyncio.start_server(handle_request, "0.0.0.0", 80)
    uasyncio.create_task(server)
    #IoHandler.buzzer_in_play()
    IoHandler.led.on()

    # start top 4 neopixel updating task
    uasyncio.create_task(neopixels())
    # main task control loop pulses red led
    counter = 0
    while True:
        if counter % 1000 == 0:
            IoHandler.set_can_reading()
            IoHandler.set_gps_reading()
            IoHandler.set_onewire_reading()
        counter += 1
        # 0 second pause to allow other tasks to run
        await uasyncio.sleep(0)

# start asyncio task and loop
try:
    # start the main async tasks
    uasyncio.run(main())
except KeyboardInterrupt:
    print('Stop button')
    #IoHandler.buzzer_in_play()
    IoHandler.led.off()
    sys.exit()
finally:
    # reset and start a new event loop for the task scheduler
    uasyncio.new_event_loop()
