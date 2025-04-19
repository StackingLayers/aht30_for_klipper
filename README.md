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
Be aware that this is not an official klipper module so adding the file will make the klipper version report as "dirty". All this means is that there is a file or modification that is not matching the main source code of klipper. Nothing is being installed in the background of your system and simply deleting the aht30.py file and the added text in the temperature_sensors.cfg will completely remove it from your system if you choose to not have it.

#Note for wireing:
The aht30 can technically be ran on 5V, but it is important to keep in mind that most mcus use 3.3v for logic level communication. If you power with 5v then the i2c output will also be 5v and this can potentially damage the microcontroller if it's not 5v tolerant. It is best to power it with 3.3V either by a dedicated 3.3V pin or using a 3.3V voltage regulator.

# Bonus circuit python script 
I have also included a circuit python script to give the option to use the Btt panda sense on a rp2040-zero (it should work with a pico too. it can also have pins changed to work with other rp2040 based boards.) This will output the temp and humidity to a serial console.

[Panda sense on circuit py_code.py](https://github.com/StackingLayers/aht30_for_klipper/blob/main/Panda%20sense%20on%20circuit%20py_code.py) 
Just remame it to code.py and drop it into the circuit python directory. 

# Show your support if you like my work.
Help support my work and use my affiliate link to [get your own Panda Sense here](https://shareasale.com/r.cfm?b=1890927&u=3691202&m=118144&urllink=biqu%2Eequipment%2Fproducts%2Fbigtreetech%2Dpanda%2Dsense%2Ddurable%2Dpp%2Dshell%2Dmagnetic%2Dplug%2Dplay%2Dhigh%2Dprecision%2Dtemperature%2Dhumidity%2Dsensing%2Dpanda%2Dtouch%2Dreal%2Dtime%2Ddisplay%2Dbambu%2Dlab%2D3d%2Dprinter%3Fgad%5Fsource%3D1%26gclid%3DCjwKCAjwk43ABhBIEiwAvvMEBzR6C1FiP0YVMUUN%5FxnPQRoo8X56S5ztux7C4o3u4FyCdWL2dd1zshoCuzIQAvD%5FBwE&afftrack=Panda%20sense)  => short link => http://shrsl.com/4vsrl
