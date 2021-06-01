# A Home Assistant custom component to get CoWin vaccination availability.
To get started put all the files from/custom_components/cowin/ here: <config directory>/custom_components/cowin/

Example configuration.yaml:

```sensor:
  - platform: cowin
    pincode: 600062
    scan_interval: 86400
