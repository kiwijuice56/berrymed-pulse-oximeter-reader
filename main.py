# https://github.com/ehborisov/BerryMed-Pulse-Oximeter-tool/blob/master/berrymed_pulse_oximeter/berrymed_pulse_oximeter.py
# https://github.com/zh2x/BCI_Protocol/blob/master/BCI%20Protocol%20V1.2.pdf

import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "00:A0:50:61:3A:8C"
RECEIVE_CHARACTERISTIC = "49535343-1E4D-4BD9-BA61-23C647249616"

async def main(address):
    async with BleakClient(address) as client:
        await client.start_notify(RECEIVE_CHARACTERISTIC, receive_data)
        await asyncio.sleep(10.0)
        await client.stop_notify(RECEIVE_CHARACTERISTIC)

def receive_data(sender, data):
    for i in data:
        # The first byte always has the msb equal to 1
        if not (data[i] & 0b10000000):
            continue

        # Once we are reading a contiguous packet, package the next 5 bytes
        packet = [data[i]]
        for j in range(i + 1, i + 5):
            if j >= len(data):
                break
            # Any other byte has the msb equal to 0
            if data[j] & 0b10000000:
                break
            packet.append(data[j])
        if not len(packet) == 5:
            continue

        labeled_data = {}

        labeled_data["pulse_rate"] = ((packet[2] & 0b01000000) << 7) | (packet[3] & 0b01111111)
        labeled_data["spo2"] = packet[4] & 0b01111111
        labeled_data["bargraph"] = packet[2] & 0b00000111

        print(labeled_data)

asyncio.run(main(DEVICE_ADDRESS))