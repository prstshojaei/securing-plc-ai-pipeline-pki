PROGRAM main
VAR
	temperature : int := 25;
	high_limit : int := 70;
	critical_limit : int := 90;
	sensor_fault : bool := FALSE;
	alarm_high : bool := FALSE;
	alarm_critical : bool := FALSE;
	system_ok : bool := TRUE;
	heater_on : bool := TRUE;
END_VAR

IF sensor_fault THEN
    alarm_high := FALSE;
    alarm_critical := FALSE;
    system_ok := FALSE;
    heater_on := FALSE;

ELSE
    IF heater_on THEN
        temperature := temperature + 1;
    ELSE
        temperature := temperature - 1;
    END_IF;

    IF temperature < 20 THEN
        heater_on := TRUE;
    END_IF;

    IF temperature > 75 THEN
        heater_on := FALSE;
    END_IF;

    alarm_high := (temperature >= high_limit);
    alarm_critical := (temperature >= critical_limit);

    system_ok := NOT alarm_critical;
END_IF;

END_PROGRAM