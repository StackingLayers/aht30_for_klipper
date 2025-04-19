# aht30_for_klipper
This is an extras module for klipper to add support for the aht30 temp and humidity sensor line that found in the btt Panda Sense

simply drop the aht30.py into the ~/klipper/klippy/extras/ directory then add 
```
# Load "AHT30"
[aht30]
```
to the ~/klipper/klippy/extras/temperature_sensors.cfg file under the aht10 one. Restart klipper and add the following to the printer.cfg
```
[temperature_sensor AHT30]
sensor_type: AHT30
i2c_mcu: EBB               # this is the mcu you are plugged in to 
i2c_bus: i2c3_PB3_PB4      # this is the i2c bus you are connected to. this can be found by clicking the mcu name in the machine settings of mainsail or fluidd.

[gcode_macro QUERY_AHT30]
description: Report temperature and humidity from the AHT30 sensor
gcode:
    {% set s = printer["aht30 AHT30"] %}
    {action_respond_info(
        "Temperature: %.2f C\n"
        "Humidity: %.2f%%" % (
            s.temperature,
            s.humidity))}
```
