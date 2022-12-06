import can
import threading
import time
import os


os.system('echo ncr18650b | sudo -S ./CAN_ON')
time.sleep(1)

channels = ['battery', 'bike']
buses = {ch: can.ThreadSafeBus(channel=ch,
                           interface='socketcan',  # noqa
                           bitrate=250000,  # noqa
                           recevie_own_messages=False)  # noqa
         for ch in channels}

print('')
print('Emptying read buffers...')
for bus in buses.values():
    bus.flush_tx_buffer()
    m = bus.recv(0.1)
    while type(m) == can.Message:
        print(m)
        m = bus.recv(0.1)

print('Read buffers empty.')


def forwarder(source, destination, blacklist):
    for msg in source:
        if msg.arbitration_id in blacklist or msg.is_error_frame:
            continue
        # if msg.arbitration_id == 0x81:
        #     msg.data[0] = 0x6e
        destination.send(msg)
        print(msg)


notImportantForBattery = {}
t1 = threading.Thread(target=forwarder, args=(buses['bike'], buses['battery'], notImportantForBattery))
t1.name = 'From bike to battery'

buses['battery'].send(can.Message())

notImportantForBike = {}
t2 = threading.Thread(target=forwarder, args=(buses['battery'], buses['bike'], notImportantForBike))
t2.name = 'From battery to bike'

threads = [t1, t2]

for t in threads:
    t.start()
