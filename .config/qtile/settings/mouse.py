from libqtile.config import Drag, Click
from libqtile.command import lazy
from settings.keybindings import SUPER

mouse = [
    Drag(
        [SUPER],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [SUPER], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([SUPER], "Button2", lazy.window.bring_to_front()),
]
