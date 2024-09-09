# Pressure Sensor Interface

This repository contains PCB designs & firmware (WIP) for an 8-channel USB pressure sensor/solenoid valve driver.

## Features

(Note that this is still in the early prototype stage so these specs have not been validated yet)

**8x pressure sensors**

- using the LWPxxx series of low-cost piezoresistive pressure sensors
- HX711 Load cell amplifier to read output
  - Note the full scale range of the pressure sensor is wider than the input range of the HX711 - This means the full range of the sensor may be impossible to read, but this is an acceptable tradeoff for the extremely low cost.
  - Capable of up to 144Hz sampling rate
 
**8x Solenoid Valve Drivers**

- Low-side NMOS switches
- Capable of ~4A per channel
- Separate DC power input for solenoid valves, supports 0-24VDC (Limited by 30V Vds rating of FET)
- Individual PWM control of each channel

**STM32F103 Microcontroller + USB-C**
