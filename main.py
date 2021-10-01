import can
import threading
import pickle
import time
import os

os.system('echo ncr18650b | sudo -S ./CAN_ON')

channels = ['can0', 'can1']
buses = [can.Bus(channel=ch,
               interface='socketcan',  # noqa
               bitrate=500000,  # noqa
               recevie_own_messages=False)  # noqa
         for ch in channels]

print('Emptying read buffers...')
for bus in buses:
    bus.flush_tx_buffer()
    msg = bus.recv(0.1)
    while type(msg) == can.Message:
        print(msg)
        msg = bus.recv(0.1)

print('Read buffers empty.')

captured = list()


def forwarder(source, destination):
    for msg in source:
        print(msg)
        destination.send(msg)
        captured.append(msg)


t1 = threading.Thread(target=forwarder, args=(buses[0], buses[1]))
t2 = threading.Thread(target=forwarder, args=(buses[1], buses[0]))

threads = [t1, t2]

for t in threads:
    t.start()

while len(captured) < 5000:
    time.sleep(1)

pickle.dump(captured, open("captured.p", "wb"))
