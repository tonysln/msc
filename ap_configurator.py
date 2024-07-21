#!/usr/bin/python3


from mqtt_alive import *

import asyncio
from textual import log
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Grid
from textual.widgets import Button, Header, Footer, Static, OptionList, Input, RadioButton, RadioSet, Label
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
WDEVICE = 'wlan0' # TODO iwconfig -> acquire device name (wlan0)


def update_static(screen, idd, text, append=False) -> None:
    """Utility function to update static screen object"""
    s = screen.query_one(f'#{idd}', Static)
    newtext = text if not append else s.renderable + text
    s.update(newtext)



class ConnectedClients(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Connected Clients
            """)
        yield Static(f"""
            Click on Scan to begin
            """, id="scanres1")
        yield Button("Scan", id="scan-btn", classes="buttons")

        yield Footer()


    async def check_connected_clients(self) -> None:
        global WDEVICE

        out = await run_arp_scan(WDEVICE)
        update_static(self, 'scanres1', f"""
            Scan result: {out}

            Total clients: {len(out.keys())}
            """)


    def on_mount(self):
        pass


    def on_button_pressed(self, event: Button.Pressed) -> None:
        asyncio.create_task(self.check_connected_clients())


class LocalConfiguration(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Configure Access Point
            """)

        yield Static('\tAP software/method/backend:')
        with RadioSet(id='ap_backend'):
            yield RadioButton("NetworkManager", value=True, id='networkmanager')
            yield RadioButton("hostapd", id="hostapd")

        yield Static('\tThe name for the network:')
        yield Input(placeholder="Network Name", id='bssid')
        yield Static('\tPassword for the network:')
        yield Input(placeholder="Password", password=True, id='netpass')

        yield Button("Configure", id="config-btn", classes="buttons")
        yield Static('\t\n', id="status")
        
        yield Footer()


    def on_mount(self):
        pass

    async def configure_local(self) -> None:
        # if broadcom -> check firmware folders, if minimal found -> apply

        backend = self.query_one('#ap_backend').pressed_button.id
        nname = self.query_one('#bssid').value
        npass = self.query_one('#netpass').value

        if not backend or not nname or not npass or len(nname) < 2 or len(nname) > 32 or len(npass) < 8 or len(npass) > 128:
            update_static(self, 'status', '\t[!] Incorrect configuration!')
            return 

        update_static(self, 'status', '\t[.] Starting configuration...')
        



    def on_button_pressed(self, event: Button.Pressed) -> None:
        asyncio.create_task(self.configure_local())


class OpenWRTConfiguration(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Configure OpenWRT Router

            Make sure your router has the following requirements met: ...
            ...

            Step 1:

            - SSID/name?: Input
            - Password: Input
            - Version/something ...


            Step 2:

            - Upload firmware from here ...
            - and/or enable SSH or something

            [Connect]

            Wait for completion... uploading settings ... updating ... 

            Restarting ...

            [Test Connection]
            """)

        yield Static('The name for the network:')
        yield Input(placeholder="Network Name")
        yield Static('Password for the network:')
        yield Input(placeholder="Password", password=True)

        yield Footer()


class APSettings(Screen):
    BINDINGS = [("m", "app.pop_screen", "Back to Menu")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("""
            # Access Point Settings

            Chosen network name: ...
            IP: ...

            MQTT IP: ...
            Type of AP software: ...

            OpenWRT? ...

            IoTempower? ...
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

            Wi-Fi chip make, model, version numbers, architecture ...

            Type of drivers you are running, firmware? 

            General system info ...


            Some information on what the support for your hardware is ...
            """)

        # TODO additional lookup for driver info, probably through modprobe

        yield Footer()


class QuitScreen(Screen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Please install and activate IoTempower before using this app!", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()



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
            yield Static("\n\n", id="detected-chip")
            yield Static("\n", id="softap-status")
            yield Static("\n\n", id="iotemp-status")
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
        yield Footer()
        

    def on_mount(self) -> None:
        self.install_screen(ConnectedClients(), name="concli")
        self.install_screen(LocalConfiguration(), name="localconf")
        self.install_screen(OpenWRTConfiguration(), name="wrtconf")
        self.install_screen(APSettings(), name="apsettings")
        self.install_screen(WiFiChipInfo(), name="wifichipinfo")
        asyncio.create_task(self.update_detected_chip())
        asyncio.create_task(self.check_iotempower())


    def confirm_chip(self, detected) -> str:
        global SOFTAP

        detected = detected.lower()

        if 'netman_available' in detected:
            SOFTAP = 'networkmanager'
        if 'hostapd_available' in detected:
            SOFTAP = 'hostapd'

        if any(x in detected for x in ['brcm', 'broadcom', 'bcm']):
            return 'Broadcom'
        if any(x in detected for x in ['iwlwifi', 'intel']):
            return 'Intel'
        if any(x in detected for x in ['rtl', 'realtek']):
            return 'Realtek'

        return ''


    async def on_option_list_option_selected(self, message: OptionList.OptionSelected) -> None:
        await self.handle_option(message.option.id)


    async def handle_option(self, option_id: str) -> None:
        if not IOTEMPOWER and not option_id == "vq":
            self.push_screen(QuitScreen())
            return

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


    async def update_detected_chip(self) -> None:
        global SYSTEM, SOFTAP, WIFI_CHIP

        update_static(self, 'detected-chip', '\t[.] Running chip detection...\n')

        proc = await asyncio.create_subprocess_shell(
            "bash ./scripts/detect_wifi_chip.sh",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        SYSTEM = platform.system()
        plfrm = platform.machine() + '-' + platform.platform(aliased=True, terse=True) + '-' + SYSTEM + '-' + platform.processor()

        if stdout and (chip := self.confirm_chip(stdout.decode())):
            WIFI_CHIP = chip
            result = '\t[+] Your Wi-Fi chip: ' + chip + '\n\t    System: ' + plfrm
        else:
            result = '\t[!] Unable to detect your Wi-Fi chip.\n\t    System: ' + plfrm

        update_static(self, 'detected-chip', result)

        #if SOFTAP:
            #update_static(self, 'softap-status', '\n\t[+] ' + SOFTAP + ' has been detected')



    async def check_iotempower(self) -> None:
        global IOTEMPOWER

        proc = await asyncio.create_subprocess_shell(
            'bash ./scripts/detect_iotempower.sh',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        IOTEMPOWER = stdout.decode() == 'yes'

        status = "\t[+] IoTempower available!" if IOTEMPOWER else "\t[-] IoTempower is not installed! Functionality is not available!"

        update_static(self, 'iotemp-status', status)

        if not IOTEMPOWER:
            self.push_screen(QuitScreen())


    def activate_brcm_minimal(self) -> None:
        pass


    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = APConfigurator()  
    app.run()
