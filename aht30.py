import logging
from .aht10 import AHT10_COMMANDS as BASE_COMMANDS, AHT10_MAX_BUSY_CYCLES
from . import bus

# AHT30 stand-alone driver for Klipper (pure ASCII source)
# --------------------------------------------------------
# * Uses same I2C address (0x38) and command bytes as AHT10
# * Skips INIT / RESET sequences because some boards NACK them
# * Default I2C bus speed is left at 100 kHz (Klipper minimum)
# * CRC-8 verified (polynomial 0x31, initial 0xFF)
# --------------------------------------------------------

AHT30_COMMANDS = BASE_COMMANDS  # address and command bytes identical
AHT30_I2C_ADDR = 0x38


def calc_crc8(data):
    """Return CRC-8 of data (poly 0x31, init 0xFF)."""
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def _safe_i2c_write(i2c, payload):
    """Write without raising on NACK. Return True if ACKed."""
    try:
        i2c.i2c_write(payload)
        return True
    except Exception:
        return False


class AHT30:
    """Klipper sensor object for the AHT30 temperature / humidity sensor."""

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.reactor = self.printer.get_reactor()
        # Klipper enforces >=100 kHz on i2c_speed, so use that default.
        self.i2c = bus.MCU_I2C_from_config(
            config, default_addr=AHT30_I2C_ADDR, default_speed=100000)
        self.report_time = config.getint('aht30_report_time', 30, minval=5)
        self.temp = self.min_temp = self.max_temp = self.humidity = 0.0
        self.sample_timer = self.reactor.register_timer(self._sample_aht30)
        self.printer.add_object('aht30 ' + self.name, self)
        self.printer.register_event_handler('klippy:connect', self.handle_connect)

    # ------------------------------- Klipper hooks --------------------------

    def handle_connect(self):
        # No INIT needed; just schedule first sample.
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, cb):
        self._callback = cb

    def get_report_time_delta(self):
        return self.report_time

    # ------------------------------ Core logic ------------------------------

    def _make_measurement(self):
        data = None
        is_busy = True
        cycles = 0

        try:
            while is_busy:
                if cycles > AHT10_MAX_BUSY_CYCLES:
                    logging.warning('aht30: device busy, skipping')
                    return False
                cycles += 1

                # Trigger single measurement
                if not _safe_i2c_write(self.i2c, AHT30_COMMANDS['MEASURE']):
                    return False
                # Wait at least 80 ms; use 110 ms like the AHT10 driver
                self.reactor.pause(self.reactor.monotonic() + 0.11)

                read = self.i2c.i2c_read([], 7)
                if read is None:
                    return False
                data = bytearray(read['response'])
                if len(data) != 7:
                    return False

                if calc_crc8(data[:6]) != data[6]:
                    logging.warning('aht30: CRC mismatch')
                    return False

                is_busy = bool(data[0] & 0x80)

        except Exception as e:
            logging.exception('aht30: measurement error: %s', str(e))
            return False

        # Convert raw values to engineering units.
        temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        self.temp = (temp_raw * 200.0 / 1048576) - 50.0
        hum_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        self.humidity = int(hum_raw * 100 / 1048576)
        if self.humidity > 100:
            self.humidity = 100
        elif self.humidity < 0:
            self.humidity = 0
        return True

    # ------------------------------ Timer loop ------------------------------

    def _sample_aht30(self, eventtime):
        if not self._make_measurement():
            self.temp = self.humidity = 0.0
            return self.reactor.NEVER

        if self.temp < self.min_temp or self.temp > self.max_temp:
            self.printer.invoke_shutdown(
                'AHT30 temperature %.1f C outside range %.1f:%.1f' % (
                    self.temp, self.min_temp, self.max_temp))

        measured_time = self.reactor.monotonic()
        print_time = self.i2c.get_mcu().estimated_print_time(measured_time)
        self._callback(print_time, self.temp)
        return measured_time + self.report_time

    # ------------------------------ Status API ------------------------------

    def get_status(self, eventtime):
        return {
            'temperature': round(self.temp, 2),
            'humidity': self.humidity,
        }


# -------------------------- Factory registration ---------------------------

def load_config(config):
    heaters = config.get_printer().lookup_object('heaters')
    heaters.add_sensor_factory('AHT30', AHT30)
