import can
import threading
import pickle
import time
import os
import analyse

runForever = False
verbose = True
record = True

os.system('echo ncr18650b | sudo -S ./CAN_ON')
time.sleep(1)

channels = ['battery', 'bike']
buses = {ch: can.ThreadSafeBus(channel=ch,
                           interface='socketcan',  # noqa
                           bitrate=500000,  # noqa
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

if not verbose:
    print('Silent mode - messages are not displayed here!')

captured = list()
run = True


def forwarder(source, destination, blacklist):
    for msg in source:
        if msg.arbitration_id in blacklist or msg.is_error_frame:
            continue
        destination.send(msg)
        if verbose:
            print(msg)
        if record and not runForever:
            captured.append(msg)
        if not run:
            break


notImportantForBattery = {0x48, 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0x202, 0x205, 0x210, 0x170, 0x131, 0xC6, 0xBE, 0xA3, 0x3B,
                          0x37, 0x9b, 0x4a, 0x30, 0x203, 0x220, 0x221, 0xa0, 0xa1, 0xa2, 0xa4, 0xa5, 0xa6, 0x9f, 0x88,
                          0x108, 0x3c, 0xc7, 0x211, 0x210, 0xbc, 0x2c0, 0x2c1, 0x171, 0xbf, 0xbd, 0x59}
t1 = threading.Thread(target=forwarder, args=(buses['bike'], buses['battery'], notImportantForBattery))
t1.name = 'From bike to battery'

buses['battery'].send(can.Message())

notImportantForBike = {0x61, 0x063D4E7E, 0xe1, 0x1c, 0x2aa, 0x101, 0x55, 0x140, 0x1d0, 0xcc, 0xcd, 0x8c, 0x151}
t2 = threading.Thread(target=forwarder, args=(buses['battery'], buses['bike'], notImportantForBike))
t2.name = 'From battery to bike'

threads = [t1, t2]

for t in threads:
    t.start()

if record:
    while len(captured) < 2000:
        time.sleep(0.1)

    pickle.dump(captured, open("captured.p", "wb"))
    analyse.analyse()

if not runForever:
    run = False
    for t in threads:
        t.join()

    print('Switching off')
