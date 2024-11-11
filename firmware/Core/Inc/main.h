/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */
struct __attribute__((packed)) TxStruct
{
  uint8_t magic[4];
  float pressures[8];
  uint32_t crc;
};

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define DOUT2_Pin GPIO_PIN_10
#define DOUT2_GPIO_Port GPIOB
#define DOUT3_Pin GPIO_PIN_11
#define DOUT3_GPIO_Port GPIOB
#define DOUT4_Pin GPIO_PIN_12
#define DOUT4_GPIO_Port GPIOB
#define DOUT5_Pin GPIO_PIN_13
#define DOUT5_GPIO_Port GPIOB
#define DOUT6_Pin GPIO_PIN_14
#define DOUT6_GPIO_Port GPIOB
#define DOUT7_Pin GPIO_PIN_15
#define DOUT7_GPIO_Port GPIOB
#define CLK_Pin GPIO_PIN_8
#define CLK_GPIO_Port GPIOA
#define PD_SCK_Pin GPIO_PIN_9
#define PD_SCK_GPIO_Port GPIOA
#define DOUT0_Pin GPIO_PIN_8
#define DOUT0_GPIO_Port GPIOB
#define DOUT1_Pin GPIO_PIN_9
#define DOUT1_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
