from libqtile import bar, widget
from libqtile.config import Screen
from settings.widgets import bar_separator, network_monitor, keyboard_layout, icon


# only left the app name
def remove_excess_info(name):
    return name.split(" - ")[-1]


def left_side_widgets():
    return [
        icon(20, " "),
        widget.GroupBox(
            highlight_method="line",
            inactive="#707880",
            font="Ubuntu Nerd Font Bold",
            disable_drag=True,
            # center_aligned=True,
            borderwidth=3,
            urgent_alert_method="text",
            urgent_border="#A54242",
            urgent_text="#A54242",
        ),
        icon(20, " "),
        widget.WindowName(
            parse_text=remove_excess_info,
            font="Ubuntu Nerd Font Regular",
        ),
    ]


def middle_side_widgets():
    return [
        widget.Spacer(),
        widget.Clock(
            format="   %a %d %b %Y   •      %H:%M:%S",
        ),
        widget.Spacer(),
    ]


def right_side_widgets():
    return [
        *keyboard_layout(),
        *bar_separator(),
        *network_monitor(),
        *bar_separator(),
        widget.Volume(
            emoji=True,
            emoji_list=["󰸈", "󰕿", "󰖀", "󰕾"],
            fontsize=20,
            volume_app="pavucontrol",
        ),
        widget.Volume(
            volume_app="pavucontrol",
        ),
        *bar_separator(),
        widget.Battery(
            format="{char}   {percent:2.0%}",
        ),
    ]


screens = [
    Screen(
        wallpaper="~/.config/qtile/darkside.png",
        # wallpaper="~/.config/qtile/win-landscape.jpg",
        wallpaper_mode="fill",
        top=bar.Bar(
            [
                *left_side_widgets(),
                *middle_side_widgets(),
                *right_side_widgets(),
            ],
            26,
            border_width=6,
        ),
    ),
]
