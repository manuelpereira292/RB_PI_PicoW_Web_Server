# Using asyncio for non blocking web server
import machine, uasyncio, sys # type: ignore
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
                response_obj = {
                    'status': 0,
                    'Data_Power': IoHandler.Get_Power_Reading(),
                    'Data_Ignition': IoHandler.Get_Ignition_Reading(),
                    'Data_CANh': IoHandler.Get_CANh_Reading(),
                    'Data_CANl': IoHandler.Get_CANl_Reading(),
                    'Data_CAN': IoHandler.Get_CAN_Reading(),
                    'Data_GPS': IoHandler.Get_GPS_Reading(),
                    'Data_OneWire': IoHandler.Get_OneWire_Reading(),
                    'Data_Temp': IoHandler.Get_Temp_Reading(),
                    'Data_Fuel': IoHandler.Get_Fuel_Reading(),
                    'Data_Door': IoHandler.Get_Door_Reading(),
                    'Data_Panic': IoHandler.Get_Panic_Reading(),
                    'Data_UDB': IoHandler.Get_UDB_Reading(),
                    'Data_Battery': IoHandler.Get_Battery_Reading(),
                    'Data_Temperature': IoHandler.Get_Temperature_Reading(),
                    'Data_Time': IoHandler.Get_Time_Reading()}
                
                response_builder.set_body_from_dict(response_obj)
            
            # Set switches reading
            elif action == 'SetSwitch':
                # Returns JSON object with states
                value = request.data()['value']
                response_obj = {
                    'status': IoHandler.Set_Switches_Reading(value),
                    'Emoji_Power': IoHandler.dict_emoji['Power'],
                    'Info_Power': IoHandler.dict_info['Power'],
                    'Emoji_Ignition': IoHandler.dict_emoji['Ignition'],
                    'Info_Ignition': IoHandler.dict_info['Ignition'],
                    'Emoji_CANh': IoHandler.dict_emoji['CANh'],
                    'Info_CANh': IoHandler.dict_info['CANh'],
                    'Emoji_CANl': IoHandler.dict_emoji['CANl'],
                    'Info_CANl': IoHandler.dict_info['CANl'],
                    'Emoji_CAN': IoHandler.dict_emoji['CAN'],
                    'Info_CAN': IoHandler.dict_info['CAN'],
                    'Emoji_GPS': IoHandler.dict_emoji['GPS'],
                    'Info_GPS': IoHandler.dict_info['GPS'],
                    'Emoji_OneWire': IoHandler.dict_emoji['OneWire'],
                    'Info_OneWire': IoHandler.dict_info['OneWire'],
                    'Emoji_Temp': IoHandler.dict_emoji['Temp'],
                    'Info_Temp': IoHandler.dict_info['Temp'],
                    'Emoji_Fuel': IoHandler.dict_emoji['Fuel'],
                    'Info_Fuel': IoHandler.dict_info['Fuel'],
                    'Emoji_Door': IoHandler.dict_emoji['Door'],
                    'Info_Door': IoHandler.dict_info['Door'],
                    'Emoji_Panic': IoHandler.dict_emoji['Panic'],
                    'Info_Panic': IoHandler.dict_info['Panic'],
                    'Emoji_UDB': IoHandler.dict_emoji['UDB'],
                    'Info_UDB': IoHandler.dict_info['UDB'],
                    'Emoji_SI': IoHandler.dict_emoji['SI'],
                    'Data_SI': IoHandler.dict_data['SI'],
                    'Info_SI': IoHandler.dict_info['SI'],
                    'Emoji_Immo': IoHandler.dict_emoji['Immo'],
                    'Data_Immo': IoHandler.dict_data['Immo'],
                    'Info_Immo': IoHandler.dict_info['Immo'],
                    'Emoji_BOut': IoHandler.dict_emoji['BOut'],
                    'Data_BOut': IoHandler.dict_data['BOut'],
                    'Info_BOut': IoHandler.dict_info['BOut'],
                    'Emoji_BIn': IoHandler.dict_emoji['BIn'],
                    'Data_BIn': IoHandler.dict_data['BIn'],
                    'Info_BIn': IoHandler.dict_info['BIn']}
                
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
    
    
    except OSError as _error:
        print('OSError: ', _error)
    except UnicodeError:
        pass
    except MemoryError:
        print('Memory error')
        IoHandler.buzzer_in_play()
        IoHandler.led.off()
        machine.reset()
    except KeyboardInterrupt:
        print('Power button')
        IoHandler.buzzer_in_play()
        IoHandler.led.off()
        sys.exit()
    except RuntimeError:
        print('Reboot button')
        IoHandler.buzzer_in_play()
        IoHandler.led.off()
        machine.reset()


# Coroutine that will run as the neopixel update task
async def task_01():
    counter = 0
    while True:
        if counter % 1000 == 0:
            IoHandler.Set_CAN_Reading()
            IoHandler.Set_GPS_Reading()
        counter += 1
        # 0 second pause to allow other tasks to run
        await uasyncio.sleep(0)


# Coroutine that will run as the neopixel update task
async def task_02():
    counter = 0
    while True:
        if counter % 1000 == 0:
            IoHandler.Set_OneWire_Reading()
            IoHandler.Set_Temp_Reading()
        counter += 1
        # 0 second pause to allow other tasks to run
        await uasyncio.sleep(0)


# main coroutine to boot async tasks
async def main():
    # start web server task
    print('Setting up webserver...')
    server = uasyncio.start_server(handle_request, "0.0.0.0", 80)
    uasyncio.create_task(server)
    
    IoHandler.buzzer_in_play()
    IoHandler.led.on()

    # Start updating other tasks
    uasyncio.create_task(task_01())
    uasyncio.create_task(task_02())
    
    # Main task control loop
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
            IoHandler.Set_Battery_Reading()
            IoHandler.Set_Temperature_Reading()
            IoHandler.Set_Time_Reading()
        counter += 1
        # 0 second pause to allow other tasks to run
        await uasyncio.sleep(0)

# Start asyncio task and loop
try:
    # Start the main async tasks
    uasyncio.run(main())
except KeyboardInterrupt:
    print('Stop button')
    IoHandler.buzzer_in_play()
    IoHandler.led.off()
    sys.exit()
finally:
    # Reset and start a new event loop for the task scheduler
    uasyncio.new_event_loop()
