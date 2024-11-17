#include "valve.h"

uint8_t valve_inited = 0;

uint8_t valve_states[N_VALVES];

uint32_t valve_timers[N_VALVES];

extern TIM_HandleTypeDef htim2, htim3;

void set_valve_pwms(void) {
    uint16_t pwm_values[8] = { 0 };

    for(uint8_t i = 0; i < N_VALVES; ++i) {
        if(valve_states[i]) {
            if(valve_timers[i] < HIT_TIME) {
                pwm_values[i] = HIT_PWM;
            } else {
                pwm_values[i] = HOLD_PWM;
            }
        } else {
            pwm_values[i] = 0;
        }
    }
    htim2.Instance->CCR1 = pwm_values[0];
    htim2.Instance->CCR2 = pwm_values[1];
    htim2.Instance->CCR3 = pwm_values[2];
    htim2.Instance->CCR4 = pwm_values[3];

    htim3.Instance->CCR1 = pwm_values[4];
    htim3.Instance->CCR2 = pwm_values[5];
    htim3.Instance->CCR3 = pwm_values[6];
    htim3.Instance->CCR4 = pwm_values[7];
}

void valve_init(void) {
    valve_inited = 1;
    for(uint8_t i = 0; i < N_VALVES; ++i) {
        valve_states[i] = 0;
        valve_timers[i] = 0;
    }
    set_valve_pwms();

    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_4);

    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_4);
}

void valve_update(void) {
    if(valve_inited == 0) {
        return;
    }
    for(uint8_t i = 0; i < N_VALVES; ++i) {
        if(valve_states[i]) {
            if(valve_timers[i] < HIT_TIME) {
                valve_timers[i]++;
            }
        } else {
            valve_timers[i] = 0;
        }
    }

    set_valve_pwms();
}