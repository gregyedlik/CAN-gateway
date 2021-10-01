import can
import threading

busM = can.Bus(channel='can0',
               interface='socketcan',  # noqa
               bitrate=500000,  # noqa
               recevie_own_messages=False)  # noqa

busK = can.Bus(channel='can1',
               interface='socketcan',  # noqa
               bitrate=500000,  # noqa
               recevie_own_messages=False)  # noqa

captured = list()


def battery2bike():
    for msg in busM:
        print(msg)
        captured.append(msg)
        busK.send(msg)

        if len(captured) > 10000:
            break


def bike2battery():
    for msg in busK:
        print(msg)
        captured.append(msg)
        busM.send(msg)

        if len(captured) > 10000:
            break


threading.Thread(target=battery2bike).start()
threading.Thread(target=bike2battery).start()

idsFromBattery = [msg.arbitration_id for msg in captured if msg.channel == 'can0']
idsFromBattery = list(dict.fromkeys(idsFromBattery))

idsFromBike = [msg.arbitration_id for msg in captured if msg.channel == 'can1']
idsFromBike = list(dict.fromkeys(idsFromBike))

for ID in idsFromBike:
    print(hex(ID))
