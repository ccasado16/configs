import configparser
import locale
from shutil import which
import subprocess
import sys
from os.path import expanduser
import uuid
import gi

gi.require_version("NM", "1.0")
# pylint: disable=no-name-in-module
from gi.repository import NM, GLib  # noqa pylint: disable=wrong-import-position


CONFIG = configparser.ConfigParser()
CONFIG.read(expanduser("~/.config/qtile/theme/networkmenu)config.ini"))
ENC = locale.getpreferredencoding()


def cli_args():
    """Don't override dmenu_cmd function arguments with CLI args. Removes -l
    and -p if those are passed on the command line.

    Exception: if -l is passed and dmenu_command is not defined, assume that the
    user wants to switch dmenu to the vertical layout and include -l.

        Returns: List of additional CLI arguments

    """
    args = sys.argv[1:]
    command = CONFIG.get("dmenu", "dmenu_command", fallback=False)

    if "-l" in args or "p" in args:
        for nope in ["-l", "-p"] if command is not False else ["-p"]:
            try:
                nope_idx = args.index(nope)
                del args[nope_idx]
            except ValueError:
                pass
    return args


def dmenu_cmd(num_lines, prompt="Networks", active_lines=None):
    """Create the dmenu command to display the different options."""

    command = ["rofi", "-dmenu", "-p", str(prompt), "-l", str(num_lines)]

    rofi_highlight = CONFIG.getboolean("dmenu", "rofi_highlight", fallback=False)

    if rofi_highlight:
        command.extend(["-a", ",".join([str(num) for num in active_lines])])

    if prompt == "Passphrase":
        command.extend(["-password"])

    return command


def choose_adapter(client):
    """Choose the network adapter to connect to the network."""

    devices = client.get_devices()
    devices = [
        device for device in devices if device.get_device_type() == NM.DeviceType.WIFI
    ]

    if not devices:
        return None

    if len(devices) == 1:
        return devices[0]

    devices_names = "\n".join([device.get_iface() for device in devices])

    selected_device = subprocess.run(
        dmenu_cmd(num_lines=len(devices), prompt="Choose a network adapter to use:"),
        capture_output=True,
        check=False,
        input=devices_names,
        encoding=ENC,
    ).stdout

    if not selected_device.strip():
        sys.exit()

    # Filter devices by selected device
    devices = [
        device for device in devices if device.get_iface() == selected_device.strip()
    ]

    # Just to make sure we have only one device
    assert len(devices) == 1

    return devices[0]


def is_installed(cmd):
    """Check if a program is installed on the system."""
    return which(cmd) is not None


def ssid_to_utf8(nm_access_point):
    """Convert binary SSID to utf-8 string."""
    ssid = nm_access_point.get_ssid()

    if not ssid:
        return ""

    ret = NM.utils_ssid_to_utf8(ssid.get_data())
    return ret


def access_point_security(nm_access_point):
    """Parse the security flags to return a string with the security type."""
    flags = nm_access_point.get_flags()
    wpa_flags = nm_access_point.get_wpa_flags()
    rsn_flags = nm_access_point.get_rsn_flags()

    security_type = ""

    # check if the access point has privacy enabled
    if (
        (flags & getattr(NM, "80211ApFlags").PRIVACY)
        and (wpa_flags == 0)
        and (rsn_flags == 0)
    ):
        security_type = "WEP"

    if wpa_flags:
        security_type = "WPA1"

    if rsn_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_PSK:
        security_type += "WPA2"

    if rsn_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_SAE:
        security_type += "WPA3"

    if (wpa_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_802_1X) or (
        rsn_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_802_1X
    ):
        security_type += "802.1X"

    if (wpa_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_OWE) or (
        rsn_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_OWE
    ):
        security_type += "OWE"

    # If there is no security, return OPEN
    if not security_type:
        security_type = "OPEN"

    return security_type.strip()


class Action:
    """Helper class to execute functions from a string variable"""

    def __init__(self, name, func, args=None, active=False):
        self.name = name
        self.func = func
        self.is_active = active

        if args is None:
            self.args = None
        elif isinstance(args, list):
            self.args = args
        else:
            self.args = [args]

    def __str__(self):
        return self.name

    def __call__(self):
        if self.args is None:
            self.func()
        else:
            self.func(*self.args)


def connection_matches_adapter(connection, adapter):
    """Return True if the connection is applicable to the adapter.

    There seem to be two ways for a connection specify what interfaceit belongs

    - By setting 'mac-address' in [wifi] to the adapter's MAC.
    - By setting 'interface-name' in [connection]to the adapter's name.

    Depending on how the connection was added, it seems like either 'mac-address' or 'interface-name' or neither of both is set.
    """

    # [wifi] mac-address
    wireless_setting = connection.get_setting_wireless()
    mac_address = wireless_setting.get_mac_address()

    if mac_address:
        return mac_address == adapter.get_permanent_hw_address()

    # [connection] interface-name
    connection_setting = connection.get_setting_connection()
    interface_name = connection_setting.get_interface_name()

    if interface_name:
        return interface_name == adapter.get_iface()

    # Neither mac-address nor interface-name is set, let's assume this connection is for multiple/all adapters
    return True


def process_access_point(nm_access_point, is_active, adapter):
    """Activate/Deactivate an access point connection and ask for the password if needed"""

    # if is actice, deactivate it
    if is_active:
        CLIENT.deactivate_connection_async(
            nm_access_point, None, notify_deactivate_connection, nm_access_point
        )
        LOOP.run()
    else:
        current_connections = [
            connection
            for connection in CONNECTIONS
            if connection.get_setting_wireless() is not None
            and connection_matches_adapter(connection, adapter)
        ]

        connection = nm_access_point.filter_connections(current_connections)

        if len(connection) == 1:
            CLIENT.activate_connection_async(
                connection[0],
                adapter,
                nm_access_point.get_path(),
                None,
                notify_activate_connection,
                nm_access_point,
            )
            LOOP.run()
        else:
            if access_point_security(nm_access_point) != "OPEN":
                password = get_password()
            else:
                password = ""

            set_new_connection(nm_access_point, password, adapter)


def notify_activate_connection(dev, res, data):
    """Notify the user if the connection was activated successfully."""
    try:
        connection = dev.activate_connection_finish(res)
    except GLib.Error:
        connection = None

    if connection:
        notify(f"Connected to {data.get_ssid()}")
    else:
        notify(f"Failed to connect to {data.get_ssid()}", urgency="critical")

    LOOP.quit()


def notify_deactivate_connection(dev, res, data):
    """Notify the user if the connection was deactivated successfully."""
    if dev.deactivate_connection_finish(res) is True:
        notify(f"Disconnected from {data.get_ssid()}")
    else:
        notify(f"Failed to disconnect from {data.get_ssid()}", urgency="critical")

    LOOP.quit()


def create_access_points_actions(
    access_points, active_access_point, active_access_point_connection, adapter
):
    """For each Access Point in a list, create the string and its attached function (activate/deactivate)"""

    active_access_point_bssid = (
        active_access_point.get_bssid() if active_access_point is not None else ""
    )

    names = [ssid_to_utf8(ap) for ap in access_points]
    max_len_name = max([len(name) for name in names]) if names else 0
    secs = [access_point_security(ap) for ap in access_points]
    max_len_sec = max([len(sec) for sec in secs]) if secs else 0

    access_points_actions = []

    for nm_access_point, name, sec in zip(access_points, names, secs):
        bars = NM.utils_wifi_strength_bars(nm_access_point.get_strength())

        wifi_chars = CONFIG.get("dmenu", "wifi_chars", fallback=False)
        if wifi_chars:
            bars = "".join([wifi_chars[i] for i, j in enumerate(bars) if j == "*"])

        is_active = nm_access_point.get_bssid() == active_access_point_bssid

        action_name = f"{name:<{max_len_name}s} {sec:<{max_len_sec}s} {bars:>4}"

        if is_active:
            access_points_actions.append(
                Action(
                    action_name,
                    process_access_point,
                    [active_access_point_connection, True, adapter],
                    active=True,
                ),
            )
        else:
            access_points_actions.append(
                Action(
                    action_name,
                    process_access_point,
                    [nm_access_point, False, adapter],
                ),
            )

    return access_points_actions


def get_password():
    """Get a password from the user using dmenu and return it as a string."""
    return subprocess.run(
        dmenu_cmd(num_lines=0, prompt="Passphrase"),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
        encoding=ENC,
    ).stdout


def set_new_connection(nm_access_point, nm_password, adapter):
    """Setup a new NetworkManager connection with the given password."""

    nm_password = str(nm_password).strip()
    profile = create_wifi_profile(nm_access_point, nm_password, adapter)
    CLIENT.add_and_active_connection_asyn(
        profile, adapter, nm_access_point.get_path(), None, verify_connection, profile
    )
    LOOP.run()


def create_wifi_profile(nm_access_point, password, adapter):
    """Create the NM profile given the AP and password"""
    # https://cgit.freedesktop.org/NetworkManager/NetworkManager/tree/examples/python/gi/add_connection.py
    # https://cgit.freedesktop.org/NetworkManager/NetworkManager/tree/examples/python/dbus/add-wifi-psk-connection.py

    access_point_sec = access_point_security(nm_access_point)
    profile = NM.SimpleConnection.new()

    s_con = NM.SettingConnection.new()
    s_con.set_property(NM.SETTING_CONNECTION_ID, ssid_to_utf8(nm_access_point))
    s_con.set_property(NM.SETTING_CONNECTION_UUID, str(uuid.uuid4()))
    s_con.set_property(NM.SETTING_CONNECTION_TYPE, "802-11-wireless")
    profile.add_setting(s_con)

    s_wifi = NM.SettingWireless.new()
    s_wifi.set_property(NM.SETTING_WIRELESS_SSID, nm_access_point.get_ssid())
    s_wifi.set_property(NM.SETTING_WIRELESS_MODE, "infrastructure")
    s_wifi.set_property(
        NM.SETTING_WIRELESS_MAC_ADDRESS, adapter.get_permanent_hw_address()
    )
    profile.add_setting(s_wifi)

    s_ip4 = NM.SettingIP4Config.new()
    s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
    profile.add_setting(s_ip4)

    s_ip6 = NM.SettingIP6Config.new()
    s_ip6.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
    profile.add_setting(s_ip6)

    if access_point_sec != "OPEN":
        s_wifi_sec = NM.SettingWirelessSecurity.new()

        if "WPA" in access_point_sec:
            if "WPA3" in access_point_sec:
                s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "sae")
            else:
                s_wifi_sec.set_property(
                    NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "wpa-psk"
                )

            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_AUTH_ALG, "open")
            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_PSK, password)

        elif "WEP" in access_point_sec:
            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "None")
            s_wifi_sec.set_property(
                NM.SETTING_WIRELESS_SECURITY_WEP_KEY_TYPE, NM.WepKeyType.PASSPHRASE
            )

            s_wifi_sec.set_wep_key(0, password)

        profile.add_setting(s_wifi_sec)

    return profile


def verify_connection(client, result, data):
    """Check if the connection completes successfully. Delete the connection if there is an error."""
    try:
        active_connection = client.add_and_activate_connection_finish(result)
        connection = active_connection.get_connection()

        if not all(
            [
                connection.verify(),
                connection.verify_secrets(),
                data.verify(),
                data.verify_secrets(),
            ]
        ):
            raise GLib.Error("Connection verification failed")
        notify(f"Connected to {data.get_ssid()}")
    except GLib.Error:
        try:
            notify(f"Failed to connect to {data.get_ssid()}", urgency="critical")
            connection.delete_async()
        except UnboundLocalError:
            pass
    finally:
        LOOP.quit()


def create_ap_list(adapter, active_connections):
    """Create the list of access points to connect to. Remove duplicate APs, keep strongest signals and the active AP

    Return: access_points - list of access points
            active_access_point - active access point
            active_access_point_connection - active access point connection
            adapter - network adapter
    """

    access_points = []
    access_points_names = []

    active_access_point = adapter.get_active_access_point()

    all_access_points = sorted(
        adapter.get_access_points(), key=lambda ap: ap.get_strength(), reverse=True
    )

    current_connections = [
        connection
        for connection in CONNECTIONS
        if connection.get_setting_wireless() is not None
        and connection_matches_adapter(connection, adapter)
    ]

    try:
        access_points_connections = active_access_point.filter_connections(
            current_connections
        )

        active_access_point_name = ssid_to_utf8(active_access_point)
        active_access_point_connection = [
            active_connection
            for active_connection in active_connections
            if active_connection.get_connection() in access_points_connections
        ]
    except AttributeError:
        active_access_point_name = None
        active_access_point_connection = []

    if len(active_access_point_connection) > 1:
        raise ValueError("Multiple connection profiles match the active access point")

    active_access_point_connection = (
        active_access_point_connection[0] if active_access_point_connection else None
    )

    for nm_access_point in all_access_points:
        access_point_name = ssid_to_utf8(nm_access_point)

        if (
            nm_access_point != active_access_point
            and access_point_name == active_access_point_name
        ):
            # Skip adding AP if it's not the active but same name as active AP
            continue
        if access_point_name not in access_points_names:
            access_points_names.append(access_point_name)
            access_points.append(nm_access_point)

    return access_points, active_access_point, active_access_point_connection, adapter


def notify(message, details=None, urgency="low"):
    """Send a notification to the user using notify-send."""

    delay = CONFIG.getint("nmdm", "rescan_delay", fallback=5)
    args = [
        "-u",
        urgency,
        "-a",
        "networkmanager-dmenu",
        "-t",
        str(delay * 1000),
        message,
    ]

    if details:
        args.append(details)

    if is_installed("notify-send"):
        subprocess.run(["notify-send"] + args, check=False)


def combine_actions(eths, aps, vpns, wgs, gsms, blues, wwan, others, saved):
    # pylint: disable=too-many-arguments
    """Combine all given actions into a list of actions.

    Args: args - eths: list of Actions
                 aps: list of Actions
                 vpns: list of Actions
                 gsms: list of Actions
                 blues: list of Actions
                 wwan: list of Actions
                 others: list of Actions
    """
    compact = CONFIG.getboolean("dmenu", "compact", fallback=False)
    empty_action = [Action("", None)] if not compact else []
    all_actions = []
    all_actions += eths + empty_action if eths else []
    all_actions += aps + empty_action if aps else []
    all_actions += vpns + empty_action if vpns else []
    all_actions += wgs + empty_action if wgs else []
    all_actions += gsms + empty_action if (gsms and wwan) else []
    all_actions += blues + empty_action if blues else []
    all_actions += wwan + empty_action if wwan else []
    all_actions += others + empty_action if others else []
    all_actions += saved + empty_action if saved else []
    return all_actions


def get_selection(all_actions):
    """Spawn dmenu for selection and execute the associated action."""
    rofi_highlight = CONFIG.getboolean("dmenu", "rofi_highlight", fallback=False)
    inp = []

    if rofi_highlight:
        inp = [str(action) for action in all_actions]
    else:
        inp = [
            ("==" if action.is_active else "  ") + str(action) for action in all_actions
        ]

    active_lines = [
        index for index, action in enumerate(all_actions) if action.is_active
    ]

    command = dmenu_cmd(len(inp), active_lines=active_lines)

    select = subprocess.run(
        command,
        capture_output=True,
        check=False,
        input="\n".join(inp),
        encoding=ENC,
    ).stdout

    if not select.rstrip():
        sys.exit()

    if rofi_highlight is False:
        action = [
            action
            for action in all_actions
            if (
                (str(action).strip() == str(select.strip()) and not action.is_active)
                or ("==" + str(action) == str(select.rstrip("\n")) and action.is_active)
            )
        ]
    else:
        action = [
            action
            for action in all_actions
            if str(action).strip() == str(select.strip())
        ]

    assert len(action) == 1, f"Selection was ambiguous: '{str(select.strip())}'"
    return action[0]


def run():
    active_connections = CLIENT.get_active_connections()
    adapter = choose_adapter(CLIENT)

    if adapter:
        # pass
        access_points_actions = create_access_points_actions(
            *create_ap_list(adapter, active_connections)
        )
    else:
        access_points_actions = []

    actions = combine_actions([], access_points_actions, [], [], [], [], [], [], [])
    select = get_selection(actions)
    select()


def main():
    global CLIENT, CONNECTIONS, LOOP

    CLIENT = NM.Client.new(None)  # NM.Client
    LOOP = GLib.MainLoop()
    CONNECTIONS = CLIENT.get_connections()

    run()


if __name__ == "__main__":
    main()
