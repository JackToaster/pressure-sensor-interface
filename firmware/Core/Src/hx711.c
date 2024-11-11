#include "hx711.h"

uint8_t pulse_count;
int32_t offsets[8];

const uint16_t dout_pins[8] = {
    DOUT0_Pin, DOUT1_Pin, DOUT2_Pin, DOUT3_Pin, DOUT4_Pin, DOUT5_Pin, DOUT6_Pin, DOUT7_Pin
};

int32_t counts[8];


void hx711_initialize(uint8_t gain_pulses) {
    pulse_count = gain_pulses;
    // send out pulses to set the gain. We don't expect anything back here.
    for(uint8_t i = 0; i < 8; ++i) {
        offsets[i] = 0;
    }
    hx711_read();
}

inline void pd_sck_high(void) {
     HAL_GPIO_WritePin(PD_SCK_GPIO_Port, PD_SCK_Pin, GPIO_PIN_SET);
}

inline void pd_sck_low(void) {
     HAL_GPIO_WritePin(PD_SCK_GPIO_Port, PD_SCK_Pin, GPIO_PIN_RESET);
}


// turn a 24-bit signed value to a 32-bit signed value
int32_t sign_extend(int32_t val_24) {
    if(val_24 & 0x800000) {
        return val_24 | 0xFF000000;
    } else {
        return val_24;
    }
}

void hx711_zero(void) {
    int32_t average_values[8] = {0};

    for(uint32_t i = 0; i < ZERO_SAMPLES; ++i) {
        hx711_read();
        for(uint8_t c = 0; c < 8; ++c){
            average_values[c] += counts[c];
        }
    }
    for(uint8_t c = 0; c < 8; ++c){
        offsets[c] -= (average_values[c] / ZERO_SAMPLES);
    }
}

void wait_for_sensors(void) {

    // wait for DOUT to go low to read data
    while (HAL_GPIO_ReadPin(DOUT0_GPIO_Port, DOUT0_Pin));
}

void hx711_read(void) {
    wait_for_sensors();
    // reset counts
    for(uint8_t i = 0; i < 8; ++i) {
        counts[i] = 0;
    }

    pd_sck_low();

    uint8_t i;
    for(i = 0; i < 24; ++i) {
        // clock sck
        pd_sck_high();
        pd_sck_low();

        // read data
        uint32_t port_val = DOUT_GPIO_Port->IDR;
        // process data
        for(uint8_t i = 0; i < 8; ++i) {
            counts[i] <<= 1;
            if(port_val & dout_pins[i]) {counts[i]++;}
        }
    }
    for(; i < pulse_count; ++i) {
        pd_sck_high();
        pd_sck_low();
    }

    for(uint8_t i = 0; i < 8; ++i) {
        counts[i] = sign_extend(counts[i]) + offsets[i];
    }
}


float hx711_get_kpa(uint8_t channel) { 
    // full scale range is +/-80mV at AVDD=5V. Since we're running on 4.299V this gets scaled down.
    float full_scale_input_voltage;
    if      (pulse_count == GAIN_32_PULSES ) { full_scale_input_voltage = (4.299/5.0) * 0.080; }
    else if (pulse_count == GAIN_64_PULSES ) { full_scale_input_voltage = (4.299/5.0) * 0.040; }
    else   /*pulse_count == GAIN_128_PULSES*/{ full_scale_input_voltage = (4.299/5.0) * 0.020; }
    

    float max_hx711_val = 0x800000;

    float input_voltage = counts[channel] / max_hx711_val * full_scale_input_voltage;

    return input_voltage * 100.0 / 0.070; // 100kPa full scale range is ~70mV
    // (really it's a range from 50-110, needs some calibration)
}