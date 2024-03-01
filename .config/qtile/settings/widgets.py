from libqtile import widget


def icon(fontsize=16, text="?"):
    return widget.TextBox(text, fontsize=fontsize)


def bar_separator():
    return (widget.TextBox("  |  ", fontsize=20),)


def keyboard_layout():
    return [
        icon(20, "󰌌"),
        widget.KeyboardLayout(
            configured_keyboards=["us", "latam"],
            display_map={"us": "en", "latam": "es"},
            font="Ubuntu Nerd Font Regular",
        ),
    ]


def network_monitor():
    return [
        widget.Net(
            format=" {down:.0f}{down_suffix}",
            scroll_fixed_width=True,
            scroll=True,
            width=72,
        ),
        widget.Net(
            format=" {up:.0f}{up_suffix}  ",
            scroll_fixed_width=True,
            scroll=True,
            width=72,
        ),
        icon(20, "󰖩"),
        widget.Wlan(
            # interface="wlan0",
            interface="wlp2s0",
            format="{percent:2.0%}  •  {essid}",
            diconnected_message=' • Disconnected'

        ),
    ]


widget_defaults = dict(
    font="Ubuntu Nerd Font Medium",
    fontsize=16,
    padding=3,
)
extension_defaults = widget_defaults.copy()
