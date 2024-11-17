#include "main.h"

#define HIT_PWM 65535
#define HOLD_PWM 32768
#define HIT_TIME 10 // ms

#define N_VALVES 8


extern uint8_t valve_states[N_VALVES];

// called at start of main
void valve_init(void);

// called in systick
void valve_update(void);