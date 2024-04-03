from libqtile.config import Key
from libqtile.command import lazy
from libqtile.utils import guess_terminal
from settings.paths import QTILE_SCRIPTS


# Mod keys
ALT = "mod1"
SUPER = "mod4"

# Applications variables
terminal = guess_terminal()
FILE_MANAGER = "thunar"

# Scripts
volume = QTILE_SCRIPTS + "volume"
brightness = QTILE_SCRIPTS + "brightness"

keys = [
    # Rofi
    Key([SUPER], "Return", lazy.spawn("rofi -show drun"), desc="Spawn rofi"),
    # Function keys: Volume --
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.spawn(f"{volume} up"),
        "Increase volume",
    ),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.spawn(f"{volume} down"),
        "Decrease volume",
    ),
    Key(
        [],
        "XF86AudioMute",
        lazy.spawn(f"{volume} toggle-mute"),
        "Mute volume",
    ),
    # Function keys: Brightness --
    Key(
        [],
        "XF86MonBrightnessUp",
        lazy.spawn(f"{brightness} up"),
        "Increase brightness",
    ),
    Key(
        [],
        "XF86MonBrightnessDown",
        lazy.spawn(f"{brightness} down"),
        "Decrease brightness",
    ),
    # Rofi
    # Key([SUPER], "Return", lazy.spawn("rofi -show drun"), "Spawn rofi"),
    # Terminal
    Key([SUPER], "t", lazy.spawn(terminal), desc="Launch terminal"),
    # File manager
    Key([SUPER], "e", lazy.spawn(FILE_MANAGER), desc="Launch file manager"),
    # WM specific keybindings --
    Key([SUPER], "q", lazy.window.kill(), desc="Kill focused window"),
    # Control Qtile
    Key([SUPER, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([SUPER, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([SUPER, "control"], "s", lazy.restart(), desc="Restart Qtile"),
    # Switch between windows
    # hjkl
    Key([SUPER], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([SUPER], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([SUPER], "j", lazy.layout.down(), desc="Move focus down"),
    Key([SUPER], "k", lazy.layout.up(), desc="Move focus up"),
    # arrow keys
    Key([SUPER], "Left", lazy.layout.left(), desc="Move focus to left"),
    Key([SUPER], "Right", lazy.layout.right(), desc="Move focus to right"),
    Key([SUPER], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([SUPER], "Up", lazy.layout.up(), desc="Move focus up"),
    # Move windows between left/rigth columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new colum.
    Key(
        [SUPER, "shift"],
        "Left",
        lazy.layout.shuffle_left(),
        desc="Move window to the left",
    ),
    Key(
        [SUPER, "shift"],
        "Right",
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([SUPER, "shift"], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([SUPER, "shift"], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction will be to screen edge - window would shrink.
    Key(
        [SUPER, "control"],
        "Left",
        lazy.layout.grow_left(),
        desc="Grow window to the left",
    ),
    Key(
        [SUPER, "control"],
        "Right",
        lazy.layout.grow_right(),
        desc="Grow window to the right",
    ),
    Key([SUPER, "control"], "Down", lazy.layout.grow_down(), desc="Grow window down"),
    Key([SUPER, "control"], "Up", lazy.layout.grow_up(), desc="Grow window up"),
    Key([SUPER], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle floating and fullscreen
    Key(
        [SUPER],
        "space",
        lazy.window.toggle_floating(),
        desc="Put the focused window to/from floating mode",
    ),
    Key(
        [SUPER],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Put the focused window to/from fullscreen mode",
    ),
    # Go to next/prev group
    Key([SUPER, ALT], "Right", lazy.screen.next_group(), desc="Move to the group "),
    Key(
        [SUPER, ALT],
        "Left",
        lazy.screen.prev_group(),
        desc="Move to the group to the left",
    ),
    # Back-n-forth groups
    Key(
        [SUPER], "b", lazy.screen.toggle_group(), desc="Move to the last visited group"
    ),
    # Change focus to other window (no rofi)
    # Key([SUPER], "Tab", lazy.layout.next(), desc="Move window focus to other window"),
    # Toggle between different layouts
    Key([SUPER], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    # Increase the space for master window at the expense of slave windows
    # Key(
    #     [SUPER],
    #     "equal",
    #     lazy.layout.increase_ratio(),
    #     desc="Increase the space for master window",
    # ),
    # Decrease the space for master window in the advantage of slave windows
    # Key(
    #     [SUPER],
    #     "minus",
    #     lazy.layout.decrease_ratio(),
    #     desc="Decrease the space for master window",
    # ),
]
