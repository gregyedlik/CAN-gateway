import pickle
import pandas


def analyse():
    captured = pickle.load(open("captured.p", "rb"))

    first_timestamp = captured[0].timestamp

    captured_important = [[hex(msg.arbitration_id), msg.channel, round(msg.timestamp - first_timestamp, 3), bytes(msg.data)] for msg in captured]
    df_full = pandas.DataFrame(data=captured_important, columns=['arbitration ID', 'source', 'timestamp', 'data'])
    df_full.to_excel('result_raw.xlsx')

    capturedFromBattery = [msg for msg in captured if msg.channel == "battery"]
    capturedFromBike = [msg for msg in captured if msg.channel == "bike"]


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
    return
