import pickle
import pandas
import binascii

def analyse():
    captured = pickle.load(open("captured.p", "rb"))

    first_timestamp = captured[0].timestamp

    def make_nice_hex_string(raw):
        string = binascii.hexlify(bytes(raw)).decode('utf-8')
        string = " ".join(string[i:i+2] for i in range(0, len(string), 2))
        return string

    captured_important = [[round(msg.timestamp - first_timestamp, 3),
                           hex(msg.arbitration_id),
                           msg.channel,
                           make_nice_hex_string(msg.data)]
                          for msg in captured]
    df_full = pandas.DataFrame(data=captured_important, columns=['timestamp', 'arbitration ID', 'source', 'data'])
    df_exciting = df_full[:500]
    df_exciting.to_excel('result_raw.xlsx', index=False)

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
    return df_exciting


df = analyse()
