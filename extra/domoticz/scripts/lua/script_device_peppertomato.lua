--
-- Vars
--
commandArray = {}

TempHumOutside = 'TempHumOutside'
TempHumInside = 'TempHumInside'

LED = 'LED'
Fan = 'Fan'
Resistor = 'Resistor'
Humidifier = 'Humidifier'
Extractor = 'Extractor'
AutoControl = 'AutoControl'
HPS = 'HPS'

DayStart = uservariables['DayStart']
DayEnd = uservariables['DayEnd']
DayStart = (DayStart ~= nil and DayStart or 16)
DayEnd = (DayEnd ~= nil and DayEnd or 7)

NightTargetTemp = uservariables['NightTargetTemp']
DayTargetTemp = uservariables['DayTargetTemp']
NightTargetHum = uservariables['NightTargetHum']
DayTargetHum = uservariables['DayTargetHum']
NightTargetTemp = (NightTargetTemp ~= nil and NightTargetTemp or 22.0)
DayTargetTemp = (DayTargetTemp ~= nil and DayTargetTemp or 25.0)
NightTargetHum = (NightTargetHum ~= nil and NightTargetHum or 55.0)
DayTargetHum = (DayTargetHum ~= nil and DayTargetHum or 75.0)
--
-- Utility functions
--

-- time, in seconds, since last device update
function time_since_update(device)
  local t1 = os.time()
  local s = otherdevices_lastupdate[device]

  local year = string.sub(s, 1, 4)
  local month = string.sub(s, 6, 7)
  local day = string.sub(s, 9, 10)
  local hour = string.sub(s, 12, 13)
  local minutes = string.sub(s, 15, 16)
  local seconds = string.sub(s, 18, 19)

  local t2 = os.time{year=year, month=month, day=day, hour=hour, min=minutes, sec=seconds}
  local difference = (os.difftime (t1, t2))

  return difference
end

-- split str with token, into a table
function string_split(str, token)
  local res = {}
  local c = 0

  for i in string.gmatch(str, token) do
    res[c] = i
    c = c + 1
  end

  return res
end

-- turn device off
function turn_off(device)
  if otherdevices[device] == 'On' then
           commandArray[device] = 'Off'
  end
end

function turn_off_no_flapping(device, flap_seconds)
  if otherdevices[device] == 'On' and time_since_update(device) > flap_seconds then
           commandArray[device] = 'Off'
  end
end

-- turn device on
function turn_on(device)
  if otherdevices[device] == 'Off' then
           commandArray[device] = 'On'
  end
end

function turn_on_no_flapping(device, flap_seconds)
  if otherdevices[device] == 'Off' and time_since_update(device) > flap_seconds then
           commandArray[device] = 'On'
  end
end

-- get device that triggered script execution
function device_that_triggered_script()
  local device = ""

  for i, v in pairs(devicechanged) do
    if (#device == 0 or #i < #device) then device = i end
  end

  return device
end

-- turn on device every X seconds for Y seconds
function turn_on_every_x_for_y(device, x, y)
  value = time_since_update(device)
  if (value >= x and otherdevices[device] == 'Off') then
    print(device.." was OFF for "..value.." seconds")
    commandArray[device] = 'On'
  elseif (otherdevices[device] == 'On' and value >= y) then
    print(device.." was ON for "..value.." seconds")
    commandArray[device] = 'Off'
  end
end

-- turn on device every X seconds
function toggle_every_x_seconds(device, x)
  value = time_since_update(device)
  if (value >= x) then
    if (otherdevices[device] == 'Off') then
      commandArray[device] = 'On'
    else
      commandArray[device] = 'Off'
    end
    print(device.." was "..commandArray[device].." for "..value.." seconds")
  end
end

-- P(roportional) Controller
-- kP - P multiplier
-- reading - input value
-- sp - set point (wanted value)
function update_p(kP, reading, sp)
  return (sp-reading)*kP
end

function is_between(value, left, right)
  if value >= left and value <= right then
    return true
  end
  return false
end

--
-- logic
--

function day_logic()
  temp = otherdevices_temperature[TempHumOutside]
  hum = otherdevices_humidity[TempHumOutside]

  turn_on(HPS)

  temp_error = update_p(1.0, temp, DayTargetTemp)
  flap_interval = 60

  if is_between(temp_error, 0.51, 9999.00) then
    turn_on_no_flapping(Resistor, flap_interval)
    turn_on_every_x_for_y(Extractor, 600, 120)
    turn_off_no_flapping(Fan, flap_interval)
  elseif is_between(temp_error, -0.50, 0.50) then
    turn_on_every_x_for_y(Extractor, 600, 120)
    turn_on_every_x_for_y(Fan, 1600, 900)
    turn_off_no_flapping(Resistor, flap_interval)
  elseif is_between(temp_error, -9999.00, -0.51) then
    --turn_on_every_x_for_y(Extractor, 500, 120)
    turn_on_no_flapping(Extractor, flap_interval)
    turn_on_every_x_for_y(Fan, 1600, 900)
    turn_off_no_flapping(Resistor, flap_interval)
  end


  hum_error = update_p(1.0, hum, DayTargetHum)
  if hum_error >= 5 then
    turn_on_no_flapping(Humidifier, flap_interval)
  elseif hum_error <= -5 then
   turn_off_no_flapping(Humidifier, flap_interval)
  end
end


function night_logic()
  temp = otherdevices_temperature[TempHumOutside]
  hum = otherdevices_humidity[TempHumOutside]

  turn_off(HPS)

  temp_error = update_p(1.0, temp, NightTargetTemp)
  flap_interval = 20

  turn_on_every_x_for_y(Fan, 4300, 60)

  if is_between(temp_error, 0.51, 9999.00) then -- below sp (inferior temp)
    turn_on_no_flapping(Resistor, flap_interval)
    turn_on_every_x_for_y(Extractor, 1200, 60)
  elseif is_between(temp_error, -0.50, 0.50) then -- optimal
    turn_on_every_x_for_y(Extractor, 900, 60)
    turn_off_no_flapping(Resistor, flap_interval)
  elseif is_between(temp_error, -9999.00, -0.51) then -- above sp
    turn_on_every_x_for_y(Extractor, 600, 60)
    turn_off_no_flapping(Resistor, flap_interval)
  end

  hum_error = update_p(1.0, hum, NightTargetHum)
  if hum_error >= 5 then
    turn_on_no_flapping(Humidifier, flap_interval)
  elseif hum_error <= -5 then
   turn_off_no_flapping(Humidifier, flap_interval)
  end

end

-- run logic
function run_logic()

  -- toggle air flow based on time of day
  hour = os.date("*t")["hour"]
  if DayStart > DayEnd then
    if (hour >= DayStart or hour < DayEnd) then
      -- day
      day_logic()
    elseif hour >= DayEnd and hour < DayStart then
      -- night
      night_logic()
    end
  end

  -- print commands
  -- for key,value in pairs(commandArray) do print(key..": "..value) end
  return commandArray
end

-- check if we want to run all this script logic
if otherdevices[AutoControl] == 'On' then
  run_logic()
end

