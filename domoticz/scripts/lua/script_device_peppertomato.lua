--
-- Vars
--
commandArray = {}

TempHumBottom = 'TempHumBottom'
TempHumMiddle = 'TempHumMiddle'

LED = 'LED'
Fan = 'Fan'
Resistor = 'Resistor'
Extractor = 'Extractor'
AutoControl = 'AutoControl'
HPS = 'HPS'
ResistorAlwaysOn = false

DayStart = 17
DayEnd = 10

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

-- turn device on
function turn_on(device)
  if otherdevices[device] == 'Off' then
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

-- run logic
function run_logic()
  tempBot = otherdevices_temperature[TempHumBottom]

  -- toggle resistor based on temperature
  if ResistorAlwaysOn then
	turn_on(Resistor)
  else
    x = 30.2
    y = 32.0
    if (tempBot >= y) then
      turn_off(Resistor)
    elseif (tempBot <= x) then
      turn_on(Resistor)
    end
  end

  -- toggle air intake/outtake if temp is high/low
  high = 29.0
  low = 26.8
  if false then
	  if tempBot >= high then
		turn_on(Fan)
		turn_on(Extractor)
	  elseif tempBot <= low then
		turn_off(Fan)
		turn_off(Extractor)
	  end
  end

  -- toggle air flow based on time of day
  hour = os.date("*t")["hour"]
  if DayStart > DayEnd then
    if (hour >= DayStart or hour < DayEnd) then
      -- day
      turn_on_every_x_for_y(Fan, 560, 3600)
      turn_on_every_x_for_y(Extractor, 1500, 1500)
      turn_on(HPS)
    elseif hour >= DayEnd and hour < DayStart then  
      -- night
      turn_off(HPS)
      turn_on_every_x_for_y(Extractor, 3600, 300)
      turn_on_every_x_for_y(Fan, 3600, 120)
    end
  end

  -- print commands
  for key,value in pairs(commandArray) do print(key..": "..value) end
  return commandArray
end

-- check if we want to run all this script logic
if otherdevices[AutoControl] == 'On' then
  run_logic()
end

