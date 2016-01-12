-- Just for reference:
-- Temperature, humidity and barometer values for other devices can be found in otherdevices_temperature['yourdevice'],otherdevices_humidity['yourdevice'] and otherdevices_barometer['yourdevice'] tables.
-- To modify an otherdevice value, you should use commandArray['UpdateDevice']='idx|nValue|sValue' where idx is the device index, nValue and sValue the values to modify (see json page for details - Domoticz API/JSON URL's)

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
ResistorAlwaysOn = false

-- run logic
function run_logic()

  -- toggle resistor based on x and y temperatures
  if ResistorAlwaysOn then
    if otherdevices[Resistor] == 'Off' then
      commandArray[Resistor] = 'On'
      print("Resistor is forced to be On")
    end
  else
    x = 29.7
    y = 30.0
    value = otherdevices_temperature[TempHumBottom]
    if (value >= y) then
      if otherdevices[Resistor] == 'On' then
        commandArray[Resistor] = 'Off'
        print("Turned Off Resistor, value:"..value)
      end
    elseif (value <= x) then
      if otherdevices[Resistor] == 'Off' then
        commandArray[Resistor] = 'On'
        print("Turned On Resistor, value:"..value)
      end
    end
  end

  -- turn fan if temp is a high already
  x = 30.0
  value = otherdevices_temperature[TempHumBottom]
  if value >= x then
    if otherdevices[Fan] == 'Off' then
      commandArray[Fan] = 'On'
      print("Turned On Fan, value:"..value)
    end
  else
    toggle_every_x_seconds(Fan, 600)
  end

  -- turn extractor if temp is a high already
  --[[x = 31.0
  value = otherdevices_temperature[TempHumBottom]
  if value >= x then
    if otherdevices[Extractor] == 'Off' then
      commandArray[Extractor] = 'On'
      print("Turned On Extractor, value:"..value)
    end
  else
    turn_on_every_x_for_y(Extractor, 600, 120)
  end
  --]]
  turn_on_every_x_for_y(Extractor, 1200, 240)

  return commandArray
end

run_logic()
