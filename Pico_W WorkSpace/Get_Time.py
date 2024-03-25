from urequests import get
from utime import ticks_ms, sleep


def view_time():
    """
    Get time over network
    """
    while True:
        try:
            start = ticks_ms()
            response = get('https://timeapi.io/api/Time/current/zone?timeZone=Europe/London')
            print('')
            #print(response.content)
            date = response.json()['date'] 
            time = response.json()['time'] 
            print(date, time)
            print('')
            print('Request took -> ' + str(ticks_ms() - start) + "ms")
            print('')
            sleep(3)

        except KeyboardInterrupt:
            break

    return date, time
