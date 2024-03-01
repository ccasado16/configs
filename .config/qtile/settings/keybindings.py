from libqtile.config import Key
from libqtile.command import lazy
from libqtile.utils import guess_terminal
from settings.paths import QTILE_SCRIPTS

terminal = guess_terminal()
FILE_MANAGER = "thunar"

ALT = "mod1"
MOD = "mod4"

keys = [
    Key(key[0], key[1], *key[2:])
    for key in [
        ([MOD], "e", lazy.spawn(FILE_MANAGER)),
        ([ALT], "Tab", lazy.spawn(QTILE_SCRIPTS + "window-switcher.sh")),
        # Switch between windows
        ([MOD], "h", lazy.layout.left(), "Move focuse to left"),
        ([MOD], "l", lazy.layout.right(), "Move focus to right"),
        ([MOD], "j", lazy.layout.down(), "Move focus down"),
        ([MOD], "k", lazy.layout.up(), "Move focus up"),
        # ([MOD], "space", lazy.layout.next(), "Move window focus to other window"),
        (
            [MOD],
            "space",
            lazy.widget["keyboardlayout"].next_keyboard(),
            "Change keyboard layout",
        ),
        # Move windows between left/rigth columns or move up/down in current stack.
        # Moving out of range in Columns layout will create new colum.
        ([MOD, "shift"], "h", lazy.layout.shuffle_left(), "Move window to the left"),
        ([MOD, "shift"], "l", lazy.layout.shuffle_right(), "Move window to the right"),
        ([MOD, "shift"], "j", lazy.layout.shuffle_down(), "Move window down"),
        ([MOD, "shift"], "k", lazy.layout.shuffle_up(), "Move window up"),
        # Grow windows. If current window is on the edge of screen and direction will be to screen edge - window would shrink.
        ([MOD, "control"], "h", lazy.layout.grow_left(), "Grow window to the left"),
        ([MOD, "control"], "l", lazy.layout.grow_right(), "Grow window to the right"),
        ([MOD, "control"], "j", lazy.layout.grow_down(), "Grow window down"),
        ([MOD, "control"], "k", lazy.layout.grow_up(), "Grow window up"),
        ([MOD], "n", lazy.layout.normalize(), "Reset all window sizes"),
        # Toggle between split and unsplit sides of stack.
        # Split = all windows displayed
        # Unsplit = 1 window displayed, like Max layout, but still with
        # multiple stack panes
        (
            [MOD, "shift"],
            "Return",
            lazy.layout.toggle_split(),
            "Toggle between split and unsplit sides of stack",
        ),
        #
        ([MOD], "Return", lazy.spawn(terminal), "Launch terminal"),
        # Toggle between different layouts as defined below
        ([MOD], "Tab", lazy.next_layout(), "Toggle between layouts"),
        ([MOD], "w", lazy.window.kill(), "Kill focused window"),
        (
            [MOD],
            "f",
            lazy.window.toggle_fullscreen(),
            "Toggle fullscreen on the focused window",
        ),
        (
            [MOD],
            "t",
            lazy.window.toggle_floating(),
            "Toggle floating on the focused window",
        ),
        ([MOD, "control"], "r", lazy.reload_config(), "Reload the config"),
        ([MOD, "control"], "q", lazy.shutdown(), "Shutdown Qtile"),
        ([MOD], "r", lazy.spawncmd(), "Spawn a command using a prompt widget"),
        # rofi
        ([MOD], "m", lazy.spawn("rofi -show drun"), "Spawn rofi"),
        # volume
        (
            [],
            "XF86AudioLowerVolume",
            lazy.spawn(QTILE_SCRIPTS + "lower-volume.sh"),
        ),
        (
            [],
            "XF86AudioRaiseVolume",
            lazy.spawn(QTILE_SCRIPTS + "raise-volume.sh"),
        ),
        ([], "Print", lazy.spawn(QTILE_SCRIPTS + "screenshot.sh"))
    ]
]
