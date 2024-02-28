#!/bin/bash
# killall -q polybar
# polybar  | tee -a /tmp/polybar.log & disown &

CONFIG_HOME="$HOME/.config"

picom --config $CONFIG_HOME/picom.conf &
# polybar &
