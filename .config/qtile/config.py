import os
import subprocess
from libqtile import qtile
from libqtile import hook

from settings.groups import groups
from settings.keybindings import keys, SUPER
from settings.layouts import floating_layout, layouts
from settings.mouse import mouse
from settings.paths import QTILE_SCRIPTS
from settings.screens import screens
from settings.widgets import extension_defaults, widget_defaults


@hook.subscribe.startup_once
def autostart():
    subprocess.call([os.path.join(QTILE_SCRIPTS, "autostart.sh")])


main = None
dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
