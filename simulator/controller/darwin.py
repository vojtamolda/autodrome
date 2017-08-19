import time
import random
import struct
import foohid
import unittest
import platform
import Quartz.CoreGraphics as CG


from .controller import SteeringWheelABC, KeyboardABC


class SteeringWheelDarwin(SteeringWheelABC):
    """ Low level virtual steering wheel implementation for macOS """
    Descriptor = (
    0x05, 0x01,  # USAGE_PAGE (Generic Desktop)
    0x09, 0x05,  # USAGE (Gamepad)
    0xa1, 0x01,  # COLLECTION (Application)
    0xa1, 0x00,  # COLLECTION (Physical)
    0x05, 0x09,  # USAGE_PAGE (Button)
    0x19, 0x01,  # USAGE_MINIMUM (Button 1)
    0x29, 0x10,  # USAGE_MAXIMUM (Button 16)
    0x15, 0x00,  # LOGICAL_MINIMUM (0)
    0x25, 0x01,  # LOGICAL_MAXIMUM (1)
    0x95, 0x10,  # REPORT_COUNT (16)
    0x75, 0x01,  # REPORT_SIZE (1)
    0x81, 0x02,  # INPUT (Data,Var,Abs)
    0x05, 0x01,  # USAGE_PAGE (Generic Desktop)
    0x09, 0x30,  # USAGE (X - Steering)
    0x09, 0x31,  # USAGE (Y - Throttle)
    0x09, 0x32,  # USAGE (R1 - Brake)
    0x09, 0x33,  # USAGE (R2 - Clutch)
    0x15, 0x81,  # LOGICAL_MINIMUM (129)
    0x25, 0x7f,  # LOGICAL_MAXIMUM (127)
    0x75, 0x08,  # REPORT_SIZE (8)
    0x95, 0x04,  # REPORT_COUNT (4)
    0x81, 0x02,  # INPUT (Data,Var,Abs)
    0xc0,  # END_COLLECTION
    0xc0  # END_COLLECTION
    )
    DescriptorFormat = '{0}B'.format(len(Descriptor))
    ReportFormat = 'B4H'

    def __init__(self, name="Tithonus Virtual Wheel"):
        self.name = name
        self.steer = self.Axis(0.0, range=(-1, +1), raw_range=(0x00, 0xff))
        self.throttle = self.Axis(0.0, range=(0, 1), raw_range=(0x00, 0xff))
        self.brake = self.Axis(0.0, range=(0, 1), raw_range=(0x00, 0xff))
        self.clutch = self.Axis(0.0, range=(0, 1), raw_range=(0x00, 0xff))
        try:
            foohid.destroy(self.name)
        except:
            pass
        descriptor = struct.pack(self.DescriptorFormat, *self.Descriptor)
        foohid.create(self.name, descriptor, "SN #NaN :)", 2, 3)

    def send(self):
        """ Send the current steer, throttle and brake values to the virtual controller """
        buttons, steer, throttle, brake, clutch = 0x00, self.steer.raw, self.throttle.raw, self.brake.raw, self.clutch.raw
        report = struct.pack(self.ReportFormat, buttons, steer, throttle, brake, clutch)
        foohid.send(self.name, report)

    def __del__(self):
        foohid.destroy(self.name)


class KeyboardDarwin(KeyboardABC):
    """ Core Graphics event based virtual keyboard implementation for macOS """
    KeyMap = {  # https://stackoverflow.com/questions/3202629/where-can-i-find-a-list-of-mac-virtual-key-codes
        'a': 0x00,  # kVK_ANSI_A
        's': 0x01,  # kVK_ANSI_S
        'd': 0x02,  # kVK_ANSI_D
        'f': 0x03,  # kVK_ANSI_F
        'h': 0x04,  # kVK_ANSI_H
        'g': 0x05,  # kVK_ANSI_G
        'z': 0x06,  # kVK_ANSI_Z
        'x': 0x07,  # kVK_ANSI_X
        'c': 0x08,  # kVK_ANSI_C
        'v': 0x09,  # kVK_ANSI_V
        'b': 0x0B,  # kVK_ANSI_B
        'q': 0x0C,  # kVK_ANSI_Q
        'w': 0x0D,  # kVK_ANSI_W
        'e': 0x0E,  # kVK_ANSI_E
        'r': 0x0F,  # kVK_ANSI_R
        'y': 0x10,  # kVK_ANSI_Y
        't': 0x11,  # kVK_ANSI_T
        '1': 0x12,  # kVK_ANSI_1
        '2': 0x13,  # kVK_ANSI_2
        '3': 0x14,  # kVK_ANSI_3
        '4': 0x15,  # kVK_ANSI_4
        '6': 0x16,  # kVK_ANSI_6
        '5': 0x17,  # kVK_ANSI_5
        '=': 0x18,  # kVK_ANSI_Equal
        '9': 0x19,  # kVK_ANSI_9
        '7': 0x1A,  # kVK_ANSI_7
        '-': 0x1B,  # kVK_ANSI_Minus
        '8': 0x1C,  # kVK_ANSI_8
        '0': 0x1D,  # kVK_ANSI_0
        ')': 0x1E,  # kVK_ANSI_RightBracket
        'o': 0x1F,  # kVK_ANSI_O
        'u': 0x20,  # kVK_ANSI_U
        '(': 0x21,  # kVK_ANSI_LeftBracket
        'i': 0x22,  # kVK_ANSI_I
        'p': 0x23,  # kVK_ANSI_P
        'l': 0x25,  # kVK_ANSI_L
        'j': 0x26,  # kVK_ANSI_J
        '\'': 0x27,  # kVK_ANSI_Quote
        'k': 0x28,  # kVK_ANSI_K
        ';': 0x29,  # kVK_ANSI_Semicolon
        '\\': 0x2A,  # kVK_ANSI_Backslash
        ',': 0x2B,  # kVK_ANSI_Comma
        '/': 0x2C,  # kVK_ANSI_Slash
        'n': 0x2D,  # kVK_ANSI_N
        'm': 0x2E,  # kVK_ANSI_M
        '.': 0x2F,  # kVK_ANSI_Period
        '`': 0x32,  # kVK_ANSI_Grave
        '*': 0x43,  # kVK_ANSI_KeypadMultiply
        '+': 0x45,  # kVK_ANSI_KeypadPlus
        '\n': 0x24,  # kVK_Return
        '\t': 0x30,  # kVK_Tab
        ' ': 0x31,  # kVK_Space
        '\b': 0x33,  # kVK_Delete
    }

    def press(self, key: str):
        """ Press a virtual keyboard key """
        self.event(key, down=True)

    def release(self, key: str):
        """ Release all pressed keys """
        self.event(key, down=False)

    def event(self, key: str, down: bool):
        """ Create a Core Graphics keyboard event and post it for macOS to process """
        try:
            event = CG.CGEventCreateKeyboardEvent(None, self.KeyMap[key.lower()], down)
            if key.isupper():
                CG.CGEventSetFlags(event, CG.kCGEventFlagMaskShift | CG.CGEventGetFlags(event))
            CG.CGEventPost(CG.kCGHIDEventTap, event)
            time.sleep(0.01)
        except KeyError:
            raise NotImplementedError("Key '{}' is not implemented".format(key))


# region Unit Tests


@unittest.skipUnless(platform.system() == 'Darwin', "Only for macOS")
class TestVirtualControllersDarwin(unittest.TestCase):

    def test_wheel(self):
        # https://yukkurigames.com/enjoyable/
        wheel = SteeringWheelDarwin()
        for _ in range(30):
            wheel.steer.value = random.uniform(-1, +1)
            wheel.throttle.value = random.uniform(0, 1)
            wheel.brake.value = random.uniform(0, 1)
            wheel.clutch.value = random.uniform(0, 1)
            wheel.send()
            time.sleep(1.0)

    def test_keyboard(self):
        keyboard = KeyboardDarwin()
        keyboard.type('Hasta la vista, baby')


#endregion
