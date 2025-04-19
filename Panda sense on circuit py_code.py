import board, busio, time

AHT30_ADDR = 0x38
CMD_MEAS = bytes((0xAC, 0x33, 0x00))

def crc8(buf):
    crc = 0xFF
    for b in buf:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc

# I²C0 on GP1/GP0  —  drop to 50 kHz
i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=50_000)
while not i2c.try_lock():
    pass
time.sleep(0.02)            # ≥5 ms after power‑up

print("AHT30 starting (no INIT)…\n")

while True:
    try:
        i2c.writeto(AHT30_ADDR, CMD_MEAS)   # trigger measurement
    except OSError:
        print("Write NACK — check pull‑ups / address jumper")
        time.sleep(1)
        continue

    time.sleep(0.09)                       # ≥80 ms conversion

    data = bytearray(7)
    try:
        i2c.readfrom_into(AHT30_ADDR, data)
    except OSError:
        print("Read NACK")
        time.sleep(1)
        continue

    if crc8(data[:6]) != data[6]:
        print("CRC error")
        continue
    if data[0] & 0x80:
        print("Busy bit still set")
        continue

    hum_raw  = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

    humidity    = hum_raw  * 100 / 1048576
    temperature = temp_raw * 200 / 1048576 - 50

    print(f"Temp: {temperature:5.2f} °C   RH: {humidity:5.1f} %")
    time.sleep(2)
