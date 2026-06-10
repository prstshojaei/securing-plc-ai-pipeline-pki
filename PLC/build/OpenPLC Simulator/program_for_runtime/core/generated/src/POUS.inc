#include "POUS.h"
#include "Config0.h"

void MAIN_init__(MAIN *data__, BOOL retain) {
  __INIT_VAR(data__->TEMPERATURE,25,retain)
  __INIT_VAR(data__->HIGH_LIMIT,70,retain)
  __INIT_VAR(data__->CRITICAL_LIMIT,90,retain)
  __INIT_VAR(data__->SENSOR_FAULT,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->ALARM_HIGH,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->ALARM_CRITICAL,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SYSTEM_OK,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->HEATER_ON,__BOOL_LITERAL(TRUE),retain)
}

// Code part
void MAIN_body__(MAIN *data__) {
  // Initialise TEMP variables

  if (__GET_VAR(data__->SENSOR_FAULT,)) {
    __SET_VAR(data__->,ALARM_HIGH,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,ALARM_CRITICAL,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SYSTEM_OK,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,HEATER_ON,,__BOOL_LITERAL(FALSE));
  } else {
    if (__GET_VAR(data__->HEATER_ON,)) {
      __SET_VAR(data__->,TEMPERATURE,,(__GET_VAR(data__->TEMPERATURE,) + 1));
    } else {
      __SET_VAR(data__->,TEMPERATURE,,(__GET_VAR(data__->TEMPERATURE,) - 1));
    };
    if ((__GET_VAR(data__->TEMPERATURE,) < 20)) {
      __SET_VAR(data__->,HEATER_ON,,__BOOL_LITERAL(TRUE));
    };
    if ((__GET_VAR(data__->TEMPERATURE,) > 75)) {
      __SET_VAR(data__->,HEATER_ON,,__BOOL_LITERAL(FALSE));
    };
    __SET_VAR(data__->,ALARM_HIGH,,(__GET_VAR(data__->TEMPERATURE,) >= __GET_VAR(data__->HIGH_LIMIT,)));
    __SET_VAR(data__->,ALARM_CRITICAL,,(__GET_VAR(data__->TEMPERATURE,) >= __GET_VAR(data__->CRITICAL_LIMIT,)));
    __SET_VAR(data__->,SYSTEM_OK,,!(__GET_VAR(data__->ALARM_CRITICAL,)));
  };

  goto __end;

__end:
  return;
} // MAIN_body__() 





