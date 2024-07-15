#!/usr/bin/python3


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
            yield Static(id="detected-chip")

        self.update_detected_chip()

    async def update_detected_chip(self) -> None:
        """Update the weather for the given city."""
        chip_widget = self.query_one("#detected-chip", Static)
        o = subprocess.run(["sudo", "bash", "./detect_wifi_chip.sh"], capture_output=True)
        ostr = str(o.stdout)
        if ostr:
            chip = Text.from_ansi(ostr)
            chip_widget.update(chip)
        else:
            chip_widget.update('')


    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = APConfigurator()
    app.run()
