#!/usr/bin/python3


import asyncio
from textual import log
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button, Header, Footer, Static, OptionList
from textual.widgets.option_list import Option, Separator
from textual.reactive import reactive
from textual.message import Message
from textual import events
import subprocess
import sys



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
        yield Footer()
        

    def on_mount(self) -> None:
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
            self.show_message("You selected Option 1")
        elif option_id == "cor":
            self.show_message("You selected Option 2")
        elif option_id == "vcc":
            self.show_message("You selected Option 3")
        elif option_id == "vas":
            self.show_message("You selected Option 4")
        elif option_id == "vci":
            self.show_message("You selected Option 5")
        elif option_id == "vq":
            self.action_quit()


    async def update_detected_chip(self) -> None:
        self.query_one("#detected-chip", Static).update('\t[.] Running chip detection...')

        proc = await asyncio.create_subprocess_shell(
            "sudo bash detect_wifi_chip.sh",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if stdout and (chip := self.confirm_chip(stdout.decode())):
            result = '\t[+] Your hardware: ' + chip
        else:
            result = '\t[!] Unable to detect your hardware (' + chip + ')'

        self.query_one("#detected-chip", Static).update(result)


    async def check_connected_clients(self) -> None:
        pass


    def activate_brcm_minimal(self) -> None:
        pass


    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = APConfigurator()  
    app.run()
