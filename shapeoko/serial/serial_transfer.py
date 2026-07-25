#!/usr/bin/env python3
"""
Serial port data transfer script.

Opens two serial ports and transfers data between them character by character.
Data received on port 1 is sent to port 2, and vice versa.
"""

import logging
import serial
import sys
import threading
from datetime import datetime
from typing import Optional


class SerialPortTransfer:
    """Manages bidirectional character-by-character transfer between two serial ports."""

    def __init__(
        self,
        port1: str,
        port2: str,
        baudrate: int = 9600,
        timeout: float = 0.1,
    ):
        """
        Initialize the serial port transfer manager.

        Args:
            port1: First serial port name (e.g., '/dev/ttyUSB0' or 'COM3')
            port2: Second serial port name
            baudrate: Baud rate for both ports (default: 9600)
            timeout: Read timeout in seconds (default: 0.1)
        """
        self.port1_name = port1
        self.port2_name = port2
        self.baudrate = baudrate
        self.timeout = timeout
        self.port1: Optional[serial.Serial] = None
        self.port2: Optional[serial.Serial] = None
        self.running = False
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging for data transfers."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_1_to_2 = f"transfer_1_to_2_{timestamp}.log"
        self.log_file_2_to_1 = f"transfer_2_to_1_{timestamp}.log"

        self.logger_1_to_2 = logging.getLogger("transfer_1_to_2")
        self.logger_2_to_1 = logging.getLogger("transfer_2_to_1")

        for logger, log_file in [
            (self.logger_1_to_2, self.log_file_1_to_2),
            (self.logger_2_to_1, self.log_file_2_to_1),
        ]:
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_file)
            logger.addHandler(handler)


    def open_ports(self) -> bool:
        """
        Open both serial ports.

        Returns:
            True if both ports opened successfully, False otherwise.
        """
        try:
            print(f"Opening port 1: {self.port1_name} at {self.baudrate} baud...")
            self.port1 = serial.Serial(
                port=self.port1_name,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            print(f"✓ Port 1 opened successfully")

            print(f"Opening port 2: {self.port2_name} at {self.baudrate} baud...")
            self.port2 = serial.Serial(
                port=self.port2_name,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            print(f"✓ Port 2 opened successfully")
            return True

        except serial.SerialException as e:
            print(f"✗ Error opening serial ports: {e}")
            self.close_ports()
            return False

    def close_ports(self) -> None:
        """Close both serial ports."""
        if self.port1 and self.port1.is_open:
            self.port1.close()
            print(f"Port 1 closed")

        if self.port2 and self.port2.is_open:
            self.port2.close()
            print(f"Port 2 closed")

    def transfer_1_to_2(self) -> None:
        """Transfer data from port 1 to port 2, character by character."""
        while self.running:
            try:
                if self.port1.in_waiting > 0:
                    char = self.port1.read(1)
                    if char:
                        self.port2.write(char)
                        #log_msg = f"Port 1 → Port 2: {char!r}"
                        #print(log_msg)
                        self.logger_1_to_2.info(char)
            except serial.SerialException as e:
                error_msg = f"Error reading from port 1: {e}"
                print(error_msg)
                self.logger_1_to_2.error(error_msg)
                self.running = False
                break

    def transfer_2_to_1(self) -> None:
        """Transfer data from port 2 to port 1, character by character."""
        while self.running:
            try:
                if self.port2.in_waiting > 0:
                    char = self.port2.read(1)
                    if char:
                        self.port1.write(char)
                        #log_msg = f"Port 2 → Port 1: {char!r}"
                        #print(log_msg)
                        self.logger_2_to_1.info(char)
            except serial.SerialException as e:
                error_msg = f"Error reading from port 2: {e}"
                print(error_msg)
                self.logger_2_to_1.error(error_msg)
                self.running = False
                break

    def start(self) -> None:
        """Start bidirectional data transfer on separate threads."""
        if not self.port1 or not self.port2:
            print("Ports not open. Call open_ports() first.")
            return

        self.running = True
        print(f"\nStarting bidirectional transfer...")
        print(f"Press Ctrl+C to stop\n")

        thread1 = threading.Thread(target=self.transfer_1_to_2, daemon=True)
        thread2 = threading.Thread(target=self.transfer_2_to_1, daemon=True)

        thread1.start()
        thread2.start()

        try:
            while self.running:
                thread1.join(timeout=0.1)
                thread2.join(timeout=0.1)
        except KeyboardInterrupt:
            print("\n\nStopping transfer...")
            self.running = False
            thread1.join(timeout=1)
            thread2.join(timeout=1)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python serial_transfer.py <port1> <port2> [baudrate]")
        print("Example: python serial_transfer.py /dev/ttyUSB0 /dev/ttyUSB1 9600")
        sys.exit(1)

    port1 = sys.argv[1]
    port2 = sys.argv[2]
    baudrate = int(sys.argv[3]) if len(sys.argv) > 3 else 9600

    transfer = SerialPortTransfer(port1, port2, baudrate)

    if transfer.open_ports():
        transfer.start()
    else:
        sys.exit(1)

    transfer.close_ports()


if __name__ == "__main__":
    main()
