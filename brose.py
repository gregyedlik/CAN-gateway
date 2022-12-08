import can
import threading
import time
import os
import pickle


# os.system('echo pass | sudo -S ./CAN_ON')
# time.sleep(1)

channels = ['kvaser', 'microchip']
buses = {ch: can.ThreadSafeBus(channel=ch,
                           interface='socketcan',  # noqa
                           bitrate=250000,  # noqa
                           recevie_own_messages=False)  # noqa
         for ch in channels}

print('')
print('Emptying read buffers...')
for bus in buses.values():
    bus.flush_tx_buffer()
    m = bus.recv(0.01)
    while type(m) == can.Message:
        m = bus.recv(0.01)

print('Read buffers empty.')

captured = list()
run = True


def forwarder(source, destination, blacklist):
    for msg in source:
        if msg.arbitration_id in blacklist or msg.is_error_frame:
            continue
        destination.send(msg)
        captured.append(msg)
        print(msg)
        if not run:
            break


notImportantForBattery = {0x201}
t1 = threading.Thread(target=forwarder, args=(buses['kvaser'], buses['microchip'], notImportantForBattery))
t1.name = 'From bike to battery'

buses['kvaser'].send(can.Message())

notImportantForBike = {}
t2 = threading.Thread(target=forwarder, args=(buses['microchip'], buses['kvaser'], notImportantForBike))
t2.name = 'From battery to bike'

threads = [t1, t2]

for t in threads:
    t.start()

while len(captured) < 500:
    time.sleep(0.1)

pickle.dump(captured, open("captured.p", "wb"))
run = False
for t in threads:
    t.join()

print('Switching off')
