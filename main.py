import can
import threading
import pickle
import time
import os
import analyse

os.system('echo ncr18650b | sudo -S ./CAN_ON')
time.sleep(1)

channels = ['battery', 'bike']
buses = {ch: can.ThreadSafeBus(channel=ch,
                           interface='socketcan',  # noqa
                           bitrate=500000,  # noqa
                           recevie_own_messages=False)  # noqa
         for ch in channels}

print('Emptying read buffers...')
for bus in buses.values():
    bus.flush_tx_buffer()
    m = bus.recv(0.1)
    while type(m) == can.Message:
        print(m)
        m = bus.recv(0.1)

print('Read buffers empty.')

captured = list()
run = True
ext_sent = False


def forwarder(source, destination):
    global ext_sent
    for msg in source:
        if msg.arbitration_id == 0x088 or msg.is_error_frame:
            continue
        if msg.arbitration_id == 0x063D4E7E:
            if not ext_sent:
                ext_sent = True
            else:
                continue
        destination.send(msg)
        print(msg)
        captured.append(msg)
        if not run:
            break


t1 = threading.Thread(target=forwarder, args=(buses['bike'], buses['battery']))
t1.name = 'From bike to battery'
t2 = threading.Thread(target=forwarder, args=(buses['battery'], buses['bike']))
t2.name = 'From battery to bike'

threads = [t1, t2]

for t in threads:
    t.start()

while len(captured) < 2000:
    time.sleep(0.1)

runForever = True

if not runForever:
    pickle.dump(captured, open("captured.p", "wb"))
    analyse.analyse()
    run = False
    for t in threads:
        t.join()

    print('Switching off')
