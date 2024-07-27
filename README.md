# APConfigurator

APConfigurator is a Python-based application designed to help configure access points (AP) on various Wi-Fi-enabled devices with IoTempower support. It provides an easy-to-use interface for setting up and managing Wi-Fi networks, making it ideal for classroom use and IoT applications.


## Features

- Configure access points using NetworkManager or hostapd.
- Configure OpenWRT routers.
- View connected clients.
- View and manage access point settings.
- View Wi-Fi chip information.
- Runs bash scripts asynchronously in the background.


## Project Structure

- ap_configurator.py: Main entry point of the application containing the APConfigurator class and the main application logic.
- config.py: Shared configuration and state variables.
- utils.py: Utility functions including asynchronous command execution.
- screens.py: Screen classes for different configuration and information views.
- style.tcss: CSS styles for the Textual app.
- scripts/: Directory containing bash scripts used for configuration and detection.

...

