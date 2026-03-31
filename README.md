# AirStrike

AirStrike is a Linux desktop application for authorized Wi-Fi security auditing.  
It provides a guided workflow for:

1. Enabling monitor mode
2. Scanning nearby access points and stations
3. Capturing WPA/WPA2 handshakes
4. Running offline password auditing with hashcat

## Legal Notice

Use this project only on networks you own or where you have explicit written permission. Unauthorized use may be illegal.

## Features

1. Tkinter GUI with separate tabs for device setup, scanning, capture, and cracking.
2. WPA handshake validation using `aircrack-ng` output from capture files.
3. Cross-distro privileged command handling (works when running as root, with `sudo`, or with `doas`).
4. Optional auto-assist deauth bursts during capture (available in UI, off by default).
5. Crack workflow protections to prevent duplicate runs from repeated button clicks.
6. Capture output written to the local `captures` directory (auto-created if missing).

## Requirements

1. Linux
2. Python 3.8+
3. Root privileges for monitor/capture operations
4. Installed tools:
   - `aircrack-ng` suite (`airmon-ng`, `airodump-ng`, `aireplay-ng`, `aircrack-ng`)
   - `hashcat`
   - `hcxpcapngtool` (recommended) or `cap2hccapx`

### Install on Debian/Ubuntu/Kali

```bash
sudo apt update
sudo apt install -y aircrack-ng hashcat hcxtools
```

## Quick Start

```bash
git clone https://github.com/<your-username>/AirStrike.git
cd AirStrike
sudo python3 main.py
```

If GUI display access fails under sudo on X11, allow root display access first:

```bash
xhost +local:root
```

## Usage Flow

1. Open Device Management and click Refresh Devices.
2. Enable monitor mode.
3. Start a scan in Network Scan and wait for targets to populate.
4. In Handshake Capture, select target, verify channel, and start capture.
5. Trigger deauth manually (or enable auto-assist checkbox if desired).
6. Wait for status to show handshake captured.
7. In Password Cracking, load captured file and start Dictionary or Brute Force mode.

## Project Structure

```text
AirStrike/
├── main.py
├── core/
│   ├── monitor.py
│   ├── scanner.py
│   ├── capture.py
│   ├── deauth.py
│   └── cracker.py
├── ui/
│   ├── app.py
│   ├── device_tab.py
│   ├── scan_tab.py
│   ├── capture_tab.py
│   └── crack_tab.py
└── utils/
    ├── commands.py
    ├── logger.py
    ├── validator.py
    └── disclaimer.py
```

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| No networks found | Wrong interface mode | Enable monitor mode and re-scan |
| Capture times out | No reconnect traffic | Send small deauth bursts and keep capture running longer |
| Handshake appears in UI but not crackable | Incomplete capture | Re-capture and confirm with `aircrack-ng <file.cap>` shows `WPA (1 handshake)` or more |
| Converter error | Missing converter tool | Install `hcxtools` or `cap2hccapx` |
| Cracking starts multiple times | Multiple button clicks | Use single run; app now locks while cracking |

## Notes for Contributors

1. Keep commits focused and small.
2. Do not commit wordlists, capture files, or generated hash artifacts.
3. Respect legal-use boundaries in examples, docs, and issues.

## Disclaimer

This project is provided for educational and authorized security testing use. The maintainers are not responsible for misuse.
