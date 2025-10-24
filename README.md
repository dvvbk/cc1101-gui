# CC1101 RF Controller GUI

A modern, comprehensive graphical user interface for controlling the CC1101 sub-1GHz RF transceiver module via serial port.

Built with CustomTkinter for a sleek, dark-themed interface with modern UI elements.

## Hardware

This GUI is designed to work with the CC1101 tool firmware from:
**https://github.com/mcore1976/cc1101-tool**

Make sure to flash your CC1101 board with the firmware from the repository above before using this GUI.

## Features

### RF Configuration
- Frequency settings (300-348 MHz, 387-464 MHz, 779-928 MHz)
- Modulation modes (2-FSK, GFSK, ASK/OOK, 4-FSK, MSK)
- TX power control (-30 to +12 dBm)
- Data rate, deviation, bandwidth configuration
- Channel and channel spacing settings

### Packet Configuration
- Sync word configuration
- Address filtering
- Packet format and length modes
- CRC, FEC, Manchester encoding
- Data whitening
- Preamble settings

### Operations
- **Transmit**: Send custom hex packets
- **Receive**: RF packet sniffer mode
- **Scan**: Frequency range scanning
- **RSSI**: Signal quality monitoring
- **Chat**: Multi-device chat mode

### Recording & Playback
- Record and replay RF frames
- RAW RF data recording
- Manual frame addition
- Non-volatile memory storage
- Bit-level visualization

### Advanced Features
- **Jamming**: Continuous RF jamming
- **Brute Force**: Garage gate attacks
- **RAW Mode**: Low-level RF sampling and playback

## Design Features

- **Modern Dark Theme**: Sleek dark interface using CustomTkinter
- **Icon-Enhanced Navigation**: Emoji icons for quick visual reference
- **Color-Coded Actions**: Intuitive color scheme (green=safe, red=danger, orange=warning)
- **Responsive Layout**: Organized tabs with scrollable content
- **Real-time Terminal**: Live command/response monitoring
- **Professional Look**: Rounded corners, smooth hover effects, modern fonts

## Installation

1. Install Python 3.7 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

This will install:
- `customtkinter` - Modern UI framework
- `pyserial` - Serial port communication

## Usage

1. Run the application:
```bash
python cc1101_gui.py
```

2. Connect to your CC1101 device:
   - Select the COM port from the dropdown
   - Choose baud rate (default: 115200)
   - Click "Connect"

3. Initialize the CC1101:
   - Click "Init CC1101" to reset with default parameters

4. Configure RF settings in the "RF Configuration" tab

5. Configure packet settings in the "Packet Configuration" tab

6. Use the "Operations" tab for TX/RX operations

7. Use the "Recording/Playback" tab for frame recording

8. Use the "Advanced" tab for jamming and brute force

## Tab Overview

### RF Configuration
Configure basic radio parameters:
- Base frequency
- Modulation type
- Frequency deviation
- Channel number and spacing
- RX bandwidth
- Data rate
- TX power

### Packet Configuration
Configure packet handling:
- Sync mode and sync word
- Address checking and device address
- Packet format and length mode
- Preamble bytes
- Enable/disable CRC, FEC, Manchester, whitening

### Operations
Main operational functions:
- **TX**: Enter hex data (max 60 bytes) and transmit
- **RX Sniffer**: Toggle packet reception mode
- **RSSI**: Get signal quality information
- **Scan**: Scan frequency range for signals
- **Chat**: Enable multi-device chat

### Recording/Playback
Record and replay RF data:
- **Normal Mode**: Record decoded packets
- **RAW Mode**: Record raw RF samples
- Add frames manually
- Show buffer contents
- Save/Load to non-volatile memory

### Advanced
Special functions:
- **Jamming**: Continuous transmission
- **Brute Force**: Automated code testing
- **Echo**: Toggle serial echo

## Terminal Output

All responses from the CC1101 device appear in the terminal at the bottom:
- Commands sent are shown in cyan with ">" prefix
- Responses appear in lime green
- Clear or copy terminal output using the buttons

## Safety Warnings

**Jamming**: Jamming radio frequencies may be illegal in your jurisdiction. Use only for authorized testing.

**Brute Force**: Only use on systems you own or have explicit permission to test.

**RF Transmission**: Ensure compliance with local RF regulations regarding frequency, power, and licensing.

## Troubleshooting

**Connection fails**:
- Check COM port selection
- Verify baud rate matches device firmware
- Ensure device drivers are installed
- Try different USB ports

**No response from device**:
- Click "Init CC1101" to reset
- Check serial cable connection
- Verify device power

**Commands not working**:
- Ensure device is connected (green status)
- Check terminal for error messages
- Verify command syntax

## Command Reference

See terminal output for command responses. Most buttons send commands automatically.

To manually send commands, modify the code or use the chat mode.

## License

This is open-source software provided as-is.

## Disclaimer

This tool is for educational and authorized testing purposes only. Users are responsible for compliance with all applicable laws and regulations regarding RF transmission in their jurisdiction.
