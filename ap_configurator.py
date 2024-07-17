#!/usr/bin/python3


from mqtt_alive import *

import asyncio
from textual import log
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button, Header, Footer, Static, OptionList
from textual.widgets.option_list import Option, Separator
from textual.reactive import reactive
from textual.message import Message
from textual.screen import Screen
from textual import events
import platform
import subprocess
import sys



WIFI_CHIP = ''
SYSTEM = ''
SOFTAP = ''
IOTEMPOWER = ''


class ConnectedClients(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Connected Clients
            """)

        # TODO run MQTT part and arp-scan separately

        # TODO iwconfig -> acquire device name (wlan0)
        dev = 'wlan0'
        out = run_arp_scan(dev) # TODO async after opening screen

        yield Static(f"""
            {out}
            """)

        yield Footer()

    def on_mount(self):
        pass


class LocalConfiguration(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Configure Access Point
            """)
        yield Footer()


class OpenWRTConfiguration(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Configure OpenWRT Router
            """)
        yield Footer()


class APSettings(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Access Point Settings
            """)

        # TODO first detect if hostapd or nm,
        # underlying iwd or wpa_supplicant etc

        yield Footer()


class WiFiChipInfo(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Wi-Fi Chip Information
            """)

        # TODO additional lookup for driver info, probably through modprobe

        yield Footer()



class APConfigurator(App):
    """Access point configuration app"""

    CSS_PATH = "style.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("""
            # Welcome to APConfigurator

            This application will help you automatically configure
            your Access Point and network settings.
            """)
            yield Static("", id="detected-chip")
            yield Static("", id="selected-option")
            yield OptionList(
                Option("Configure Access Point", id="cap"),
                Option("Configure OpenWRT Router", id="cor"),
                Separator(),
                Option("View Connected Clients", id="vcc"),
                Option("View AP Settings", id="vas"),
                Option("View Wi-Fi Chip Information", id="vci"),
                Separator(),
                Option("Quit", id="vq"),
                id="menu"
            )
        yield Static("", id="softap-status")
        yield Footer()
        

    def on_mount(self) -> None:
        self.install_screen(ConnectedClients(), name="concli")
        self.install_screen(LocalConfiguration(), name="localconf")
        self.install_screen(OpenWRTConfiguration(), name="wrtconf")
        self.install_screen(APSettings(), name="apsettings")
        self.install_screen(WiFiChipInfo(), name="wifichipinfo")
        asyncio.create_task(self.update_detected_chip())


    def confirm_chip(self, detected) -> str:
        detected = detected.lower()

        if any(x in detected for x in ['brcm', 'broadcom', 'bcm']):
            return 'Broadcom'
        if any(x in detected for x in ['iwlwifi', 'intel']):
            return 'Intel'
        if any(x in detected for x in ['rtl', 'realtek']):
            return 'Realtek'

        return ''


    async def on_option_list_option_selected(self, message: OptionList.OptionSelected) -> None:
        await self.handle_option(message.option.id)


    def show_message(self, message: str) -> None:
        self.query_one("#selected-option", Static).update('\t' + message)


    async def handle_option(self, option_id: str) -> None:
        if option_id == "cap":
            self.push_screen('localconf')
        elif option_id == "cor":
            self.push_screen('wrtconf')
        elif option_id == "vcc":
            self.push_screen('concli')
        elif option_id == "vas":
            self.push_screen('apsettings')
        elif option_id == "vci":
            self.push_screen('wifichipinfo')
        elif option_id == "vq":
            self.action_quit()


    async def detect_softap(self) -> str:
        res1 = subprocess.run(['cat', '/etc/hostapd'], capture_output=True, text=True)
        res1 = res1.stdout

        res2 = subprocess.run(['grep', '-i', 'renderer', '/etc/netplan/*.yaml'], capture_output=True, text=True)
        res2 = res2.stdout

        res3 = subprocess.run(['systemctl', 'status', 'NetworkManager'], capture_output=True, text=True)
        res3 = res3.stdout

        res4 = subprocess.run(['hostapd'], capture_output=True, text=True)
        res4 = res4.stdout

        res5 = subprocess.run(['nmcli'], capture_output=True, text=True)
        res5 = res5.stdout

        out = ', '.join([res1, res2, res3, res4, res5])
        return out


    async def update_detected_chip(self) -> None:
        global SYSTEM, SOFTAP, WIFI_CHIP

        self.query_one("#detected-chip", Static).update('\t[.] Running chip detection...')

        proc = await asyncio.create_subprocess_shell(
            "sudo bash ./scripts/detect_wifi_chip.sh",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        SYSTEM = platform.system()
        plfrm = platform.machine() + '-' + platform.platform(aliased=True, terse=True) + '-' + SYSTEM + '-' + platform.processor()

        if stdout and (chip := self.confirm_chip(stdout.decode())):
            WIFI_CHIP = chip
            result = '\t[+] Your hardware: ' + chip + ': ' + plfrm
        else:
            result = '\t[!] Unable to detect your Wi-Fi chip. System: ' + plfrm

        # softap_detected = await self.detect_softap()
        # self.query_one("#softap-status", Static).update(softap_detected)

        self.check_iotempower()

        self.query_one("#detected-chip", Static).update(result)


    async def check_connected_clients(self) -> None:
        pass


    async def check_iotempower(self) -> None:
        global IOTEMPOWER

        proc = await asyncio.create_subprocess_shell(
            'echo $IOTEMPOWER_ACTIVE',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if stdout:
            IOTEMPOWER = "IoTempower activated!"
        else:
            IOTEMPOWER = "IoTempower not activated!"

        self.query_one("#softap-status", Static).update(str(IOTEMPOWER))


    def activate_brcm_minimal(self) -> None:
        pass


    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = APConfigurator()  
    app.run()
