#!/usr/bin/env python3
# -------------------------------------------------------------
# FluidNC 6-x + XHC WHB04B-6 full-function bridge
# -------------------------------------------------------------
# Based on LinuxCNC xhc-whb04b-6 component protocol specification
# https://github.com/LinuxCNC/linuxcnc/tree/master/src/hal/user_comps/xhc-whb04b-6
# -------------------------------------------------------------
# Usage:
#   python3 fluidnc_whb04b_full.py                 # normal mode (sends to serial)
#   python3 fluidnc_whb04b_full.py --debug         # debug mode (prints to terminal)
#   python3 fluidnc_whb04b_full.py -h              # show all options
# -------------------------------------------------------------
import sys, time, struct, argparse
import hid                # pip install hidapi
import serial             # pip install pyserial

# -----------------------------------------------------------------
# USER CONFIGURATION  (edit these values for your setup)
# -----------------------------------------------------------------
PENDANT_VID = 0x10CE          # XHC Technology
PENDANT_PID = 0xEB93          # WHB04B-6 (also accepted by WHB04B-4)

# Serial port that goes to the 6-x FluidNC board
#   Linux:   /dev/ttyUSB0   (or /dev/ttyUSB1, …)
#   Windows: COM3   (or whatever `mode` shows)
SERIAL_PORT = "/dev/ttyUSB0"          # <-- CHANGE THIS
SERIAL_BAUDRATE = 115200              # FluidNC default

# -----------------------------------------------------------------
# JOG SETTINGS
# -----------------------------------------------------------------
# How many millimetres the wheel-delta should move an axis per "click".
# The 6-x config (6x.config.yaml) has steps_per_mm = 320.
# The LinuxCNC component reports a signed int8_t delta (-128...+127).
# We map one click = 1 mm (change if you want finer/coarser).
JOG_INCREMENT_MM = 1.0

# Base increment for the 4th axis (rotary axis A).
# Rotary axes use steps per degree, so this is degrees per click.
# Typical: 10 steps/degree with 2000 steps/rev = 0.5 deg per step
# Adjust based on your rotary axis configuration.
JOG_INCREMENT_DEG = 1.0  # degrees per click for A axis

# Default jog feedrate (mm/min) - used for $J= commands
DEFAULT_JOG_FEEDRATE_MM_MIN = 1000

# Feedrate adjustment steps (mm/min)
FEEDRATE_STEP_SMALL = 100    # Feed+ / Feed-
FEEDRATE_STEP_LARGE = 500    # Fn+Feed+ / Fn+Feed-

# -----------------------------------------------------------------
# DEBUG COUNTERS
# -----------------------------------------------------------------
# In debug mode, these counters track simulated position per axis.
# They are sent to the pendant so the LCD updates.
DEBUG_COUNTERS_ENABLED = True

# -----------------------------------------------------------------
# PENDANT REPORT STRUCTURE (from LinuxCNC xhc-whb04b-6)
# 8 bytes received from pendant:
#   byte0: report_id (0x04)
#   byte1: random/seed
#   byte2: button1_keycode
#   byte3: button2_keycode
#   byte4: feed_rotary_keycode
#   byte5: axis_rotary_keycode
#   byte6: jog_dial_delta (signed int8_t)
#   byte7: checksum (random ^ seed)
# -----------------------------------------------------------------
REPORT_FORMAT = struct.Struct('<BBBBBBbb')  # 8 bytes: 6 uint8, 1 int8, 1 int8 (checksum)

# -----------------------------------------------------------------
# KEY CODE DEFINITIONS (from LinuxCNC README)
# -----------------------------------------------------------------
class KeyCode:
    # Button key codes (bytes 2, 3)
    NONE = 0x00
    RESET = 0x01          # Macro-11
    STOP = 0x02           # Macro-12
    START_PAUSE = 0x03    # Macro-13
    FEED_PLUS = 0x04      # Macro-1
    FEED_MINUS = 0x05     # Macro-2
    SPINDLE_PLUS = 0x06   # Macro-3
    SPINDLE_MINUS = 0x07  # Macro-4
    MACHINE_HOME = 0x08   # Macro-5
    SAFE_Z = 0x09         # Macro-6
    WORKPIECE_HOME = 0x0a # Macro-7
    SPINDLE_ON_OFF = 0x0b # Macro-8
    FN = 0x0c             # Function modifier key
    PROBE_Z = 0x0d        # Macro-9
    CONTINUOUS = 0x0e     # Macro-15 (MPG mode)
    STEP = 0x0f           # Macro-16 (Step mode)
    MACRO10 = 0x10        # Macro-10 / Macro-14

    # Axis rotary key codes (byte 5)
    AXIS_OFF = 0x06
    AXIS_X = 0x11
    AXIS_Y = 0x12
    AXIS_Z = 0x13
    AXIS_A = 0x14
    AXIS_B = 0x15
    AXIS_C = 0x16

    # Feed rotary key codes (byte 4)
    FEED_0_001 = 0x0d     # 0.001 / 2%
    FEED_0_01 = 0x0e      # 0.01 / 5%
    FEED_0_1 = 0x0f       # 0.1 / 10%
    FEED_1 = 0x10         # 1 / 30%
    FEED_60 = 0x1a        # 60%
    FEED_100 = 0x1b       # 100%
    FEED_LEAD = 0x1c      # Lead mode


# -----------------------------------------------------------------
# AXIS ROTARY STATE
# -----------------------------------------------------------------
class AxisRotary:
    """Maps axis rotary keycode to axis name and index"""
    MAP = {
        KeyCode.AXIS_X: ('X', 0),
        KeyCode.AXIS_Y: ('Y', 1),
        KeyCode.AXIS_Z: ('Z', 2),
        KeyCode.AXIS_A: ('A', 3),
        KeyCode.AXIS_B: ('B', 4),
        KeyCode.AXIS_C: ('C', 5),
        KeyCode.AXIS_OFF: (None, None),
    }

    @staticmethod
    def from_keycode(code):
        return AxisRotary.MAP.get(code, (None, None))


# -----------------------------------------------------------------
# FEED ROTARY STATE
# -----------------------------------------------------------------
class FeedRotary:
    """Maps feed rotary keycode to increment multiplier"""
    # LinuxCNC Button Text values (actual increment multipliers):
    # speed_0_001 (0x0d) = 0.001
    # speed_0_01  (0x0e) = 0.01
    # speed_0_1   (0x0f) = 0.1
    # speed_1     (0x10) = 1.0
    # percent_60  (0x1a) = 0.6 (60%)
    # percent_100 (0x1b) = 1.0 (100%)
    # lead        (0x1c) = 1.0
    MULTIPLIER = {
        KeyCode.FEED_0_001: 0.001,
        KeyCode.FEED_0_01: 0.01,
        KeyCode.FEED_0_1: 0.1,
        KeyCode.FEED_1: 1.0,
        KeyCode.FEED_60: 0.6,
        KeyCode.FEED_100: 1.0,
        KeyCode.FEED_LEAD: 1.0,
    }

    @staticmethod
    def multiplier(code):
        return FeedRotary.MULTIPLIER.get(code, 1.0)


# -----------------------------------------------------------------
# BUTTON MACRO MAP - FluidNC Commands
# Based on: http://wiki.fluidnc.com/en/features/supported_gcodes
# and: http://wiki.fluidnc.com/en/config/control
#
# LinuxCNC: "Any button pressed in combination with the modifier button
# generates an alternative event - Macro-n (with n being the macro number).
# This holds for any button, even if Macro-n is not written on the button."
#
# Note: Some functions (Feed/Spindle Override) are not standard G-codes.
# They are typically handled via real-time characters or UI commands.
# We use the closest FluidNC equivalents.
# -----------------------------------------------------------------

# Real-time characters (sent as raw bytes over serial)
RT_RESET = b'\x18'      # Ctrl-X = Soft Reset
RT_FEED_HOLD = b'!'     # ! = Feed Hold / Pause
RT_CYCLE_START = b'~'   # ~ = Cycle Start / Resume

# Primary macro map (without Fn) - keycode -> command bytes or G-code string
# Commands starting with RT_ are sent as raw bytes (real-time characters)
PRIMARY_MACRO = {
    KeyCode.RESET: RT_RESET,              # Reset → Soft Reset (Ctrl-X)
    KeyCode.STOP: RT_FEED_HOLD,           # Stop → Feed Hold (!)
    KeyCode.START_PAUSE: RT_CYCLE_START,  # Start/Pause → Cycle Start (~)
    KeyCode.SPINDLE_PLUS: b'$SOR=+10\n',  # Spindle Override +10%
    KeyCode.SPINDLE_MINUS: b'$SOR=-10\n', # Spindle Override -10%
    KeyCode.MACHINE_HOME: b'$H\n',        # Machine Home → $H (Home All)
    KeyCode.SAFE_Z: b'G53 G0 Z0\n',       # Safe Z → Machine Z=0
    KeyCode.WORKPIECE_HOME: b'G28\n',     # Workpiece Home → G28 (Predefined pos)
    KeyCode.SPINDLE_ON_OFF: b'M3\n',      # Spindle On/Off → M3 (CW) / M5 on alt
    KeyCode.PROBE_Z: b'G38.2 Z-50\n',     # Probe Z → Probe toward workpiece
    KeyCode.CONTINUOUS: b'$JG=1\n',       # Continuous/MPG mode
    KeyCode.STEP: b'$JG=0\n',             # Step mode
    KeyCode.MACRO10: b'M99\n',            # Macro 10 → User macro (example)
}

# Alternate macro map (with Fn held) - keycode -> command bytes
# LinuxCNC: "Any button pressed in combination with the modifier button
# generates an alternative event - Macro-n"
ALTERNATE_MACRO = {
    KeyCode.RESET: b'$RST=MANUAL\n',      # Fn+Reset → Manual reset
    KeyCode.STOP: b'M0\n',                # Fn+Stop → M0 (Pause)
    KeyCode.START_PAUSE: b'M1\n',         # Fn+Start → M1 (Optional stop)
    KeyCode.SPINDLE_PLUS: b'$SOR=+25\n',  # Fn+Spindle+ → +25%
    KeyCode.SPINDLE_MINUS: b'$SOR=-25\n', # Fn+Spindle- → -25%
    KeyCode.MACHINE_HOME: b'G28.1\n',     # Fn+M-Home → Set home position
    KeyCode.SAFE_Z: b'G30\n',             # Fn+Safe-Z → G30 (2nd predefined pos)
    KeyCode.WORKPIECE_HOME: b'G30\n',     # Fn+W-Home → G30
    KeyCode.SPINDLE_ON_OFF: b'M5\n',      # Fn+S-On/Off → Spindle Stop
    KeyCode.PROBE_Z: b'G38.3 Z-50\n',     # Fn+Probe-Z → Probe away
    KeyCode.CONTINUOUS: b'$JG=2\n',       # Fn+Continuous → MPG mode
    KeyCode.STEP: b'$JG=3\n',             # Fn+Step → Jog mode
    KeyCode.MACRO10: b'M98\n',            # Fn+Macro10 → Call macro
}

# Special handling buttons
SPECIAL_BUTTONS = {
    KeyCode.FN: None,  # Fn is a modifier, handled separately
}


# -----------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------
def parse_report(data):
    """Parse 8-byte pendant report into a structured dict"""
    # hidapi returns a list of ints, convert to bytes
    if isinstance(data, list):
        data = bytes(data)
    if len(data) < 8:
        return None
    # Unpack: 6 uint8, 1 int8 (delta), 1 int8 (checksum)
    r = struct.unpack('<BBBBBBbb', data[:8])
    return {
        'report_id': r[0],           # 0x04
        'random': r[1],              # seed
        'button1': r[2],             # button 1 keycode
        'button2': r[3],             # button 2 keycode
        'feed_rotary': r[4],         # feed rotary keycode
        'axis_rotary': r[5],         # axis rotary keycode
        'jog_delta': r[6],           # signed int8_t jog dial delta
        'checksum': r[7],            # checksum
    }


def mm_to_grbl_line(axis, delta_mm, increment, feedrate=None):
    """Produce a $J=G91 G21 incremental jog line with feedrate, e.g. $J=G91 G21 X1 F1000"""
    d = round(delta_mm * increment, 4)
    # Handle negative zero
    if abs(d) < 0.0001:
        d = 0.0
    if feedrate is None:
        feedrate = DEFAULT_JOG_FEEDRATE_MM_MIN
    return f"$J=G91 G21 {axis}{d} F{feedrate}"


# -----------------------------------------------------------------
# PENDANT STATE MACHINE
# -----------------------------------------------------------------
class PendantState:
    """Tracks pendant state: selected axis, feed multiplier, Fn held, etc."""

    # Axes that are rotary (use degree increment) vs linear (use mm increment)
    ROTARY_AXES = {'A', 'B', 'C'}

    def __init__(self, base_increment, rotary_increment):
        self.base_increment = base_increment       # mm per click for linear axes
        self.rotary_increment = rotary_increment   # degrees per click for rotary axes
        self.selected_axis = 'X'                   # default axis
        self.axis_index = 0
        self.feed_multiplier = 1.0
        self.fn_held = False
        self.last_button1 = KeyCode.NONE
        self.last_button2 = KeyCode.NONE
        self.last_feed_rotary = KeyCode.FEED_1
        self.last_axis_rotary = KeyCode.AXIS_OFF
        self.last_jog_delta = 0

        # Jog feedrate (mm/min)
        self.jog_feedrate = DEFAULT_JOG_FEEDRATE_MM_MIN

        # Debug counters (simulated position per axis)
        self.debug_counters = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'A': 0.0, 'B': 0.0, 'C': 0.0}

    def current_increment(self):
        """Current jog increment = base * feed_multiplier (uses correct increment for axis type)"""
        if self.selected_axis in self.ROTARY_AXES:
            return self.rotary_increment * self.feed_multiplier
        return self.base_increment * self.feed_multiplier

    def current_jog_feedrate(self):
        """Current jog feedrate (mm/min)"""
        return self.jog_feedrate

    def adjust_jog_feedrate(self, delta_mm_min):
        """Adjust jog feedrate by delta, clamped to reasonable range"""
        self.jog_feedrate = max(10, min(10000, self.jog_feedrate + delta_mm_min))
        return self.jog_feedrate

    def _update_debug_counter(self, axis, delta, increment):
        """Update debug counter for the given axis"""
        self.debug_counters[axis] += delta * increment

    def get_debug_counters(self):
        """Return debug counters dict"""
        return self.debug_counters

    def update(self, report):
        """Update state from new report, return list of commands to send"""
        commands = []

        # Track Fn modifier state (from button1 or button2)
        fn_pressed = (report['button1'] == KeyCode.FN or
                      report['button2'] == KeyCode.FN)

        # Check for axis rotary change
        if report['axis_rotary'] != self.last_axis_rotary:
            axis_name, axis_idx = AxisRotary.from_keycode(report['axis_rotary'])
            if axis_name:
                self.selected_axis = axis_name
                self.axis_index = axis_idx
                # Axis changed - could send a status command here
                # print(f"[AXIS] Selected: {axis_name}")
            self.last_axis_rotary = report['axis_rotary']

        # Check for feed rotary change
        if report['feed_rotary'] != self.last_feed_rotary:
            self.feed_multiplier = FeedRotary.multiplier(report['feed_rotary'])
            # print(f"[FEED] Multiplier: {self.feed_multiplier}")
            self.last_feed_rotary = report['feed_rotary']

        # Handle jog dial delta - apply to CURRENTLY SELECTED AXIS only
        if report['jog_delta'] != 0:
            delta = report['jog_delta']  # signed int8_t
            inc = self.current_increment()
            # LinuxCNC: "Continuous mode means n jog dial events are translated to
            # move joint n times with speed x whereas step mode to move joint n steps"
            # We use continuous mode: each delta = one increment
            axis = self.selected_axis
            if axis:
                commands.append(mm_to_grbl_line(axis, delta, inc, self.current_jog_feedrate()))
                # Update debug counter in debug mode
                if DEBUG_COUNTERS_ENABLED:
                    self._update_debug_counter(axis, delta, inc)
            self.last_jog_delta = report['jog_delta']

        # Handle button presses (button1 and button2)
        # LinuxCNC: buttons generate pressed/released events
        # We detect rising edge (press) and falling edge (release)
        for btn_name, btn_code in [('button1', report['button1']), ('button2', report['button2'])]:
            last_code = self.last_button1 if btn_name == 'button1' else self.last_button2

            if btn_code != last_code:
                # State changed
                if btn_code != KeyCode.NONE:
                    # Button PRESSED
                    if btn_code == KeyCode.FN:
                        self.fn_held = True
                    elif btn_code == KeyCode.FEED_PLUS:
                        # Feed+ : increase jog feedrate
                        new_fr = self.adjust_jog_feedrate(FEEDRATE_STEP_SMALL if not self.fn_held else FEEDRATE_STEP_LARGE)
                        if DEBUG_COUNTERS_ENABLED:
                            print(f"[FEED] Jog feedrate: {new_fr} mm/min")
                    elif btn_code == KeyCode.FEED_MINUS:
                        # Feed- : decrease jog feedrate
                        new_fr = self.adjust_jog_feedrate(-FEEDRATE_STEP_SMALL if not self.fn_held else -FEEDRATE_STEP_LARGE)
                        if DEBUG_COUNTERS_ENABLED:
                            print(f"[FEED] Jog feedrate: {new_fr} mm/min")
                    else:
                        # Regular button press - check if Fn is held
                        macro_map = ALTERNATE_MACRO if self.fn_held else PRIMARY_MACRO
                        if btn_code in macro_map:
                            commands.append(macro_map[btn_code])
                        elif btn_code in SPECIAL_BUTTONS:
                            pass  # handled elsewhere
                        else:
                            # Unknown button - could log it
                            pass
                else:
                    # Button RELEASED
                    if last_code == KeyCode.FN:
                        self.fn_held = False
                    # Other buttons on release - usually no action needed

                # Update last state
                if btn_name == 'button1':
                    self.last_button1 = btn_code
                else:
                    self.last_button2 = btn_code

        return commands


# -----------------------------------------------------------------
# PENDANT DISPLAY PACKET (Host -> Pendant)
# LinuxCNC xhc-whb04b-6 protocol (from usb.cc/usb.h and README.md):
# - Output report ID: 0x06 (HID feature report / SET_REPORT)
# - 3 blocks of 7 bytes each = 21 bytes total payload
# - Sent via HID control transfer (SET_REPORT) with report ID 0x06
# - Exact byte layout per protocol table in README.md:
#   0x00-0x01: header (uint16) = 0xfdfe
#   0x02:     seed (uint8) = 0xfe
#   0x03:     displayModeFlags (uint8)
#   0x04-0x05: axis1 integer (uint16)
#   0x06-0x07: axis1 fraction (15 bits) + sign (1 bit) = uint16
#   0x08-0x09: axis2 integer (uint16)
#   0x0A-0x0B: axis2 fraction (15 bits) + sign (1 bit) = uint16
#   0x0C-0x0D: axis3 integer (uint16)
#   0x0E-0x0F: axis3 fraction (15 bits) + sign (1 bit) = uint16
#   0x10-0x11: feedRate (uint16)
#   0x12-0x13: spindleFeedRate (uint16)
#   0x14:     padding (uint8)
#   Total: 21 bytes = 3 blocks × 7 bytes
# -----------------------------------------------------------------

# Exact struct format for 21-byte payload (little-endian):
# header(H) seed(B) flags(B)
# ax1_int(H) ax1_frac_sign(H)
# ax2_int(H) ax2_frac_sign(H)
# ax3_int(H) ax3_frac_sign(H)
# feedRate(H) spindleRate(H) padding(B)
# = 2+1+1 + 2+2 + 2+2 + 2+2 + 2+2+1 = 21 bytes
_PENDANT_PAYLOAD_FMT = struct.Struct('<H B B H H H H H H H H B')

# Display mode flags (from linuxcnc DisplayModeFlags union)
_DISP_FLAG_STEP_CONT = 0x00
_DISP_FLAG_STEP_STEP = 0x01
_DISP_FLAG_STEP_MPG  = 0x02
_DISP_FLAG_STEP_XXX  = 0x03
_DISP_FLAG_RESET     = 0x40
_DISP_FLAG_MACHINE   = 0x80


def _encode_axis(value):
    """Encode float coordinate to (integer, fraction_sign) per protocol.
    Fraction is 15 bits (value * 10000), sign is 1 bit (0=pos, 1=neg).
    Packed into a single uint16: bits 0-14 = fraction (0-9999), bit 15 = sign.
    """
    abs_val = abs(value)
    sign = 0 if value >= 0 else 1
    scaled = int(round(abs_val * 10000.0))
    integer = scaled // 10000
    fraction = scaled % 10000
    frac_sign = (fraction & 0x7FFF) | (sign << 15)
    return integer, frac_sign


def build_pendant_dro_packet(counters, selected_axis='X', seed=0xfe):
    """Build pendant display packet(s) for LCD update.
    
    Returns list of 3 blocks (7 bytes each) ready for HID transfer with report ID 0x06.
    Uses debug counters for the currently selected axis group.
    Protocol: 21 bytes = 3 blocks of 7 bytes, report ID 0x06 prepended to each.
    
    Axis selection logic:
    - If A, B, or C selected: display A, B, C positions
    - If X, Y, Z, or OFF selected: display X, Y, Z positions
    """
    # Determine which axis group to display based on selected axis
    rotary_axes = {'A', 'B', 'C'}
    linear_axes = {'X', 'Y', 'Z'}
    
    if selected_axis in rotary_axes:
        # Display A, B, C positions
        axis1_val = counters.get('A', 0.0)
        axis2_val = counters.get('B', 0.0)
        axis3_val = counters.get('C', 0.0)
    else:
        # Display X, Y, Z positions (default for X, Y, Z, OFF)
        axis1_val = counters.get('X', 0.0)
        axis2_val = counters.get('Y', 0.0)
        axis3_val = counters.get('Z', 0.0)
    
    # Encode coordinates (4 bytes each: int16 + frac_sign uint16)
    ax1_int, ax1_frac_sign = _encode_axis(axis1_val)
    ax2_int, ax2_frac_sign = _encode_axis(axis2_val)
    ax3_int, ax3_frac_sign = _encode_axis(axis3_val)
    
    # Build 21-byte payload
    # Format: <H B B H H H H H H H H B
    # header(H) seed(B) flags(B)
    # ax1_int(H) ax1_frac_sign(H)
    # ax2_int(H) ax2_frac_sign(H)
    # ax3_int(H) ax3_frac_sign(H)
    # feedRate(H) spindleRate(H) padding(B)
    # = 2+1+1 + 2+2 + 2+2 + 2+2 + 2+2+1 = 21 bytes
    payload = struct.pack(
        '<H B B H H H H H H H H B',
        0xfdfe,      # header (uint16)
        0xfe,        # seed (uint8)
        0x00,        # display flags (uint8) - step mode CONT, workpiece coords, no reset
        ax1_int, ax1_frac_sign,   # axis 1
        ax2_int, ax2_frac_sign,   # axis 2
        ax3_int, ax3_frac_sign,   # axis 3
        0,            # feedRate (uint16)
        0,            # spindleFeedRate (uint16)
        0             # padding (uint8)
    )
    
    # Split into 3 blocks of 7 bytes
    return [payload[i:i+7] for i in range(0, 21, 7)]


def send_pendant_display(pendant, blocks):
    """Send display blocks to pendant via HID feature report (report ID 0x06)"""
    for block in blocks:
        # Prepend report ID 0x06
        report = bytes([0x06]) + block
        try:
            pendant.send_feature_report(report)
        except Exception:
            # Fallback: try write (some HID devices accept output reports on default endpoint)
            try:
                pendant.write(report)
            except Exception:
                pass  # Silently ignore if pendant doesn't support display updates


# -----------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="FluidNC 6-x + XHC WHB04B-6 full-function bridge (LinuxCNC protocol)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--debug", "-d", action="store_true",
        help="Debug mode: print generated commands to terminal instead of sending over serial"
    )
    parser.add_argument(
        "--port", "-p", default=SERIAL_PORT,
        help="Serial port for FluidNC 6-x board"
    )
    parser.add_argument(
        "--baud", "-b", type=int, default=SERIAL_BAUDRATE,
        help="Baud rate for serial connection"
    )
    parser.add_argument(
        "--increment", "-i", type=float, default=JOG_INCREMENT_MM,
        help="Base jog increment in mm per wheel click (linear axes)"
    )
    parser.add_argument(
        "--rotary-increment", "-r", type=float, default=JOG_INCREMENT_DEG,
        help="Base jog increment in degrees per wheel click (rotary A/B/C axes)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output (show axis/feed changes)"
    )
    args = parser.parse_args()

    # Apply CLI overrides
    serial_port = args.port
    serial_baud = args.baud
    base_increment = args.increment
    rotary_increment = args.rotary_increment
    debug_mode = args.debug
    verbose = args.verbose

    # --- open the pendant HID device -------------------------------------------------
    try:
        pendant = hid.device()
        pendant.open(PENDANT_VID, PENDANT_PID)
        pendant.set_nonblocking(True)
        print(f"[+] Opened pendant HID device: VID=0x{PENDANT_VID:04X} PID=0x{PENDANT_PID:04X}")
    except Exception as e:
        print(f"[!] Could not open pendant HID device: {e}")
        print()
        print("    This is usually a permissions issue. The device files are owned by root.")
        print("    Fix by installing the udev rule (run as root):")
        print("      sudo cp 99-whb04b-pendant.rules /etc/udev/rules.d/")
        print("      sudo udevadm control --reload-rules && sudo udevadm trigger")
        print("    Or temporarily (until reboot):")
        print("      sudo chmod 666 /dev/bus/usb/<bus>/<device>")
        print("      sudo chmod 666 /dev/hidraw*")
        print("    (Find the correct bus/device with: lsusb | grep 10ce:eb93)")
        sys.exit(1)

    # --- open the serial pipe to the 6-x board -----------------------------------------
    ser = None
    if not debug_mode:
        try:
            ser = serial.Serial(serial_port, serial_baud, timeout=0.1)
            print(f"[+] Opened serial port: {serial_port} @ {serial_baud}")
        except Exception as e:
            print(f"[!] Could not open serial port {serial_port}: {e}")
            sys.exit(1)
    else:
        print("[*] DEBUG MODE: serial output disabled (commands printed to terminal)")

    print("[*] Full-featured bridge started - WHB04B-6 <-> FluidNC 6-x (LinuxCNC protocol)")
    print(f"    Base jog increment: {base_increment} mm per click")
    print("    Wheel jogs currently selected axis")
    print("    Axis rotary selects X/Y/Z/A/B/C")
    print("    Feed rotary sets jog increment multiplier")
    print("    Fn key enables alternate macros (Macro-11+)")
    print("    LCD shows X position (auto-report)")
    print("    Ctrl-C to quit\n")

    # -----------------------------------------------------------------
    # Enable FluidNC automatic reporting
    # -----------------------------------------------------------------
    if not debug_mode and ser:
        ser.write(b"$Report/Interval=100\n")    # 100 ms = 10 updates/sec
        ser.flush()
        time.sleep(0.2)
        response = ser.readline().decode('ascii', errors='replace').strip()
        if response:
            print(f"[FluidNC] {response}")

    # Initialize pendant state machine
    state = PendantState(base_increment, rotary_increment)

    # -----------------------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------------------
    try:
        while True:
            # ---- 1. Read pendant HID report ---------------------------------
            report_data = pendant.read(64)
            if report_data and len(report_data) >= 8:
                report = parse_report(report_data)
                if report and report['report_id'] == 0x04:
                    commands = state.update(report)
                    for line in commands:
                        if debug_mode:
                            if isinstance(line, bytes):
                                print(f"{line.decode('ascii')}")
                            else:
                                print(f"{line}")
                        else:
                            if isinstance(line, bytes):
                                ser.write(line)
                            else:
                                ser.write((line + "\n").encode('ascii'))
                    # tiny pause so the board has time to process
                    time.sleep(0.005)

            # ---- 2. Read FluidNC automatic-report line -----------------------
            if not debug_mode and ser and ser.in_waiting:
                raw = ser.readline().decode('ascii', errors='replace').strip()
                if raw.startswith('<') and raw.endswith('>'):
                    # Parse <Idle|MPos:X,Y,Z|FS:...|Ov:...>
                    parts = raw.split('|')
                    if len(parts) >= 2:
                        mpos_part = parts[1]
                        if mpos_part.startswith('MPos:'):
                            _, xyz = mpos_part.split(':', 1)
                            try:
                                x_str, y_str, z_str = xyz.split(',')
                                x, y, z = map(float, (x_str, y_str, z_str))
                            except ValueError:
                                pass
                            else:
                                # Build pendant display packet (3 blocks of 7 bytes each)
                                blocks = build_pendant_dro_packet(
                                    counters={'X': x, 'Y': y, 'Z': z},
                                    selected_axis=state.selected_axis
                                )
                                send_pendant_display(pendant, blocks)
                                if debug_mode or verbose:
                                    print(f"[DRO] X={x:8.3f}  Y={y:8.3f}  Z={z:8.3f}  | inc={state.current_increment():.4f}  axis={state.selected_axis}")

            # ---- 3. Debug mode: periodically send debug counters to pendant ---
            if debug_mode and DEBUG_COUNTERS_ENABLED:
                # Send debug counters to pendant every ~100ms
                # This makes the pendant LCD update with the simulated positions
                counters = state.get_debug_counters()
                # Build packet with debug counters for current axis group
                blocks = build_pendant_dro_packet(counters, selected_axis=state.selected_axis)
                send_pendant_display(pendant, blocks)
                if verbose:
                    print(f"[DEBUG] Counters: X={counters['X']:.3f}  Y={counters['Y']:.3f}  Z={counters['Z']:.3f}  A={counters['A']:.3f}")

            time.sleep(0.001)  # small nap

    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        pendant.close()
        if ser:
            ser.close()

if __name__ == "__main__":
    main()