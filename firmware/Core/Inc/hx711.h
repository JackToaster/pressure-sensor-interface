#ifndef __HX711_H__
#define __HX711_H__
#include "main.h"

#define GAIN_32_PULSES 26
#define GAIN_64_PULSES 27
#define GAIN_128_PULSES 25

#define ZERO_SAMPLES 64


#define DOUT_GPIO_Port DOUT0_GPIO_Port
#define DOUT_MASK (DOUT0_Pin | DOUT1_Pin | DOUT2_Pin | DOUT3_Pin | DOUT4_Pin | DOUT5_Pin | DOUT6_Pin | DOUT7_Pin)

void hx711_initialize(uint8_t gain_pulses);

void hx711_zero(void);

void hx711_read(void);

float hx711_get_kpa(uint8_t channel);

#endif