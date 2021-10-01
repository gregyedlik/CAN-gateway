import pickle
import pandas

captured = pickle.load(open("captured.p", "rb"))

capturedFromBattery = [msg for msg in captured if msg.channel == "can0"]
capturedFromBike = [msg for msg in captured if msg.channel == "can1"]


def count(cap):
    ids = [msg.arbitration_id for msg in cap]
    unique = dict.fromkeys(ids)
    counted = {hex(ID): ids.count(ID) for ID in unique}
    return counted


countedBatteryIDs = count(capturedFromBattery)
countedBikeIDs = count(capturedFromBike)

df = pandas.DataFrame(data=[countedBatteryIDs.keys(),
                            countedBatteryIDs.values(),
                            countedBikeIDs.keys(),
                            countedBikeIDs.values()],
                      index=['BatteryID', 'Count', 'BikeID', 'Count'])

df = df.transpose()

df.to_excel('results.xlsx')

print(df)

