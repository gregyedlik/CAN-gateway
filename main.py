import can
import threading
import pickle

bus1 = can.Bus(channel='can0',
               interface='socketcan',  # noqa
               bitrate=500000,  # noqa
               recevie_own_messages=False)  # noqa
bus1.flush_tx_buffer()

bus2 = can.Bus(channel='can1',
               interface='socketcan',  # noqa
               bitrate=500000,  # noqa
               recevie_own_messages=False)  # noqa
bus2.flush_tx_buffer()

captured = list()


def forwarder(source, destination):
    for msg in source:
        print(msg)
        destination.send(msg)
        captured.append(msg)
        if len(captured) > 10000:
            return


t1 = threading.Thread(target=forwarder, args=(bus1, bus2))
t2 = threading.Thread(target=forwarder, args=(bus2, bus1))

t1.start()
t2.start()

t1.join()
t2.join()

pickle.dump(captured, open("captured.p", "wb"))
