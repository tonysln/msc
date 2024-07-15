#!/usr/bin/python3


import asyncio
from textual import log
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button, Header, Footer, Static
from textual import events
import subprocess
import sys



class APConfigurator(App):
    """Access point configuration app"""

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            yield Static("""
            # Welcome to AutoConfig

            This application will help you automatically configure
            your Access Point and network settings.

            Press 'q' to quit or any other key to continue...
            """)
            yield Static("", id="detected-chip")
        

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


    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = APConfigurator()
    app.run()
