# Using asyncio for non blocking web server
import uasyncio, sys # type: ignore
from Library.WiFiConnection import WiFiConnection
from Library.RequestParser import RequestParser
from Library.ResponseBuilder import ResponseBuilder
from Library.IoHandler import IoHandler


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
                vbatValue = IoHandler.get_vbat_reading()
                pot_value = IoHandler.get_pot_reading()
                temperatureValue = IoHandler.get_temperature_reading()
                timeValue = IoHandler.get_time_reading()
                temp_value = IoHandler.get_temp_reading()

                response_obj = {
                    'status': 0,
                    'vrValue': IoHandler.Get_Power_Reading(),
                    'amValue': IoHandler.Get_Ignition_Reading(),
                    'canhValue': IoHandler.Get_CANh_Reading(),
                    'canlValue': IoHandler.Get_CANl_Reading(),
                    'canValue': IoHandler.Get_CAN_Reading(),
                    'gpsValue': IoHandler.Get_GPS_Reading(),
                    'onewireValue': IoHandler.Get_OneWire_Reading(),
                    'ds18x20Value': IoHandler.Get_Temp_Reading(),
                    'brValue': IoHandler.Get_Fuel_Reading(),
                    'ctValue': IoHandler.Get_Door_Reading(),
                    'azValue': IoHandler.Get_Panic_Reading(),
                    'rsValue': IoHandler.Get_UDB_Reading(),
                    
                    'vbatValue': vbatValue,
                    'pot_value': pot_value,
                    'temperatureValue': temperatureValue,
                    'timeValue': timeValue,
                    'temp_value': temp_value}
                
                response_builder.set_body_from_dict(response_obj)
            
            # Set switches reading
            elif action == 'SetSwitch':
                # Returns JSON object with states
                value = request.data()['value']
                response_obj = {
                    'status': IoHandler.Set_Switches_Reading(value),
                    'Emoji_Power': IoHandler.dict_emoji['Power'],
                    'Emoji_Ignition': IoHandler.dict_emoji['Ignition'],
                    'Emoji_CANh': IoHandler.dict_emoji['CANh'],
                    'Emoji_CANl': IoHandler.dict_emoji['CANl'],
                    'Emoji_CAN': IoHandler.dict_emoji['CAN'],
                    'Emoji_GPS': IoHandler.dict_emoji['GPS'],
                    'Emoji_OneWire': IoHandler.dict_emoji['OneWire'],
                    'Emoji_Temp': IoHandler.dict_emoji['Temp'],
                    'Emoji_Fuel': IoHandler.dict_emoji['Fuel'],
                    'Emoji_Door': IoHandler.dict_emoji['Door'],
                    'Emoji_Panic': IoHandler.dict_emoji['Panic'],
                    'Emoji_UDB': IoHandler.dict_emoji['UDB'],
                    'Emoji_SI': IoHandler.dict_emoji['SI'],
                    'Emoji_Immo': IoHandler.dict_emoji['Immo'],
                    'Emoji_BOut': IoHandler.dict_emoji['BOut'],
                    'Emoji_BIn': IoHandler.dict_emoji['BIn'],
                    }
                
                response_builder.set_body_from_dict(response_obj)

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
    except UnicodeError:
        pass
    except MemoryError:
        pass
    except KeyboardInterrupt:
        print('Power button')
        IoHandler.buzzer_in_play()
        IoHandler.led.off()
        sys.exit()
    except RuntimeError:
        print('Reboot button')
        IoHandler.buzzer_in_play()
        IoHandler.led.off()
        IoHandler.machine.reset()


# coroutine that will run as the neopixel update task
async def neopixels():

    counter = 0
    while True:
        if counter % 1000 == 0:
            IoHandler.Set_Power_Reading()
            IoHandler.Set_Ignition_Reading()
            IoHandler.Set_CANh_Reading()
            IoHandler.Set_CANl_Reading()
            IoHandler.Set_Fuel_Reading()
            IoHandler.Set_Door_Reading()
            IoHandler.Set_Panic_Reading()
            IoHandler.Set_UDB_Reading()

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
            IoHandler.Set_CAN_Reading()
            IoHandler.Set_GPS_Reading()
            IoHandler.Set_OneWire_Reading()
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
