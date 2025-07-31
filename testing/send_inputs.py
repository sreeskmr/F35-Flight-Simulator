import RPi.GPIO as GPIO
import socket
import json
import time
import spidev
import threading
from encoder import RotaryEncoder

# === ENCODER CONFIG ===
ENC_PIN_A = 13
ENC_PIN_B = 26
ENC_PPR = 600
ENC_IN_PER_REV = 2.0
ENC_MAX_TRAVEL = 5.0
ENC_BUTTON_THRESHOLD_LOW = 1.0   # VJoy Button A
ENC_BUTTON_THRESHOLD_MID = 4.3   # VJoy Button B
ENC_BUTTON_THRESHOLD_HIGH = 4.5 # VJoy Button C


encoder = RotaryEncoder(ENC_PIN_A, ENC_PIN_B, ENC_PPR)

def enc_inches(counts):
    return (counts / ENC_PPR) * ENC_IN_PER_REV

def enc_percent(pos):
    if pos <= 0:
        return 0
    elif pos >= ENC_MAX_TRAVEL:
        return 100
    return round((pos / ENC_MAX_TRAVEL) * 100)

# === NETWORK CONFIG ===
def get_pc_ip():
    try:
        with open("/home/pi/pc_ip.txt", "r") as f:
            return f.read().strip()
    except:
        return "127.0.0.1"

PC_IP = get_pc_ip()
PORT = 49000

# === BUTTON CONFIG ===
GPIO.setmode(GPIO.BCM)

SINGLE_BUTTONS = {
    "T1": 17,
    "T6_AutoSTO": 16,
    "T10_Button": 18,
    "T12_PitchOverride": 12
}

T2_INPUTS = [24, 14]
T2_OUTPUTS = [15, 25]
T2_DIRECTION_MAP = {(14, 15): "Left", (24, 25): "Right"}
T2_LONG_PRESS_TIME = 1.0

T3_CHANNEL_X = 1
T3_CHANNEL_Y = 0
T4_CHANNEL = 2
T5_CHAFF_PIN = 5
T5_FLARE_PIN = 6
T8_CHANNEL_ALPHA = 4
T8_CHANNEL_BETA = 5
T9_TOP_PIN = 22
T9_BOTTOM_PIN = 23
T11_STD_PIN = 27
T11_NVG_PIN = 21

VJOY_BUTTON_ORDER = [
    "T1", "T2_Left", "T2_Right", "T2_Up", "T2_Down", "T2_Center",
    "T3_Up", "T3_Down", "T3_Left", "T3_Right",
    "T4_Accel", "T4_Decel",
    "T5_Chaff", "T5_Flare", "T5_Auto",
    "T6_AutoSTO",
    "T8_ScrollUp", "T8_ScrollDown",
    "T9_Top", "T9_Center", "T9_Bottom",
    "T10_Button",
    "T11_Standard", "T11_NVG", "T11_Off",
    "T12_PitchOverride",
]

# === INIT ===
for pin in SINGLE_BUTTONS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in T2_INPUTS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in T2_OUTPUTS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

GPIO.setup(T5_CHAFF_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(T5_FLARE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(T9_TOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(T9_BOTTOM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(T11_STD_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(T11_NVG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) | adc[2]

def convert_to_voltage(value, vref=3.3):
    return (value * vref) / 1023

def read_voltage(channel):
    return convert_to_voltage(read_channel(channel))

def get_direction(voltage):
    if voltage < 1.0:
        return 0
    elif voltage > 2.2:
        return 1
    else:
        return -1

def classify_scroll(v):
    if v < 0.5:
        return 0
    elif v > 2.5:
        return 1
    else:
        return -1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
left_hold_start = None
prev_t8_state = -1
prev_throttle = -1
prev_buttons = [0] * len(VJOY_BUTTON_ORDER)

def main_loop():
    global prev_throttle, prev_t8_state, left_hold_start, prev_buttons

    try:
        while True:
            states = {key: 0 for key in VJOY_BUTTON_ORDER}

            # === ENCODER ===
            enc_count = encoder.get_count()
            enc_inches_pos = enc_inches(enc_count)
            THROTTLE = enc_percent(enc_inches_pos)
            # === ENCODER BUTTON-STYLE INPUT ===


            for name, pin in SINGLE_BUTTONS.items():
                if GPIO.input(pin) == GPIO.LOW:
                    states[name] = 1

            detected = None
            is_left_pressed = False
            for out_pin in T2_OUTPUTS:
                GPIO.output(out_pin, GPIO.LOW)
                for in_pin in T2_INPUTS:
                    if GPIO.input(in_pin) == GPIO.LOW:
                        if (in_pin, out_pin) in [(14, 15), (15, 14)]:
                            is_left_pressed = True
                        else:
                            direction = T2_DIRECTION_MAP.get((in_pin, out_pin)) or T2_DIRECTION_MAP.get((out_pin, in_pin))
                            if direction:
                                detected = direction
                GPIO.output(out_pin, GPIO.HIGH)

            if is_left_pressed:
                if left_hold_start is None:
                    left_hold_start = time.time()
                elif time.time() - left_hold_start >= T2_LONG_PRESS_TIME:
                    detected = "Center"
            else:
                if left_hold_start and time.time() - left_hold_start < T2_LONG_PRESS_TIME:
                    detected = "Left"
                left_hold_start = None

            if GPIO.input(25) == GPIO.LOW and GPIO.input(14) == GPIO.LOW:
                detected = "Down"
            if GPIO.input(15) == GPIO.LOW and GPIO.input(24) == GPIO.LOW:
                detected = "Up"
            if detected:
                states[f"T2_{detected}"] = 1

            x = get_direction(read_voltage(T3_CHANNEL_X))
            y = get_direction(read_voltage(T3_CHANNEL_Y))
            if x == 0: states["T3_Left"] = 1
            elif x == 1: states["T3_Right"] = 1
            if y == 0: states["T3_Up"] = 1
            elif y == 1: states["T3_Down"] = 1

            v4 = read_voltage(T4_CHANNEL)
            if v4 < 1.0:
                states["T4_Accel"] = 1
            elif v4 > 2.6:
                states["T4_Decel"] = 1

            if GPIO.input(T5_CHAFF_PIN) == GPIO.LOW:
                states["T5_Chaff"] = 1
            elif GPIO.input(T5_FLARE_PIN) == GPIO.LOW:
                states["T5_Flare"] = 1
            else:
                states["T5_Auto"] = 1

            va = read_voltage(T8_CHANNEL_ALPHA)
            vb = read_voltage(T8_CHANNEL_BETA)
            da = classify_scroll(va)
            db = classify_scroll(vb)
            logic = da if da == db else -1
            if logic != prev_t8_state:
                if logic == 0:
                    states["T8_ScrollUp"] = 1
                    print("↑ Scroll Up")
                elif logic == 1:
                    states["T8_ScrollDown"] = 1
                    print("↓ Scroll Down")
                prev_t8_state = logic
            if logic == -1:
                prev_t8_state = -1

            if GPIO.input(T9_BOTTOM_PIN) == GPIO.LOW and GPIO.input(T9_TOP_PIN) == GPIO.HIGH:
                states["T9_Bottom"] = 1
            elif GPIO.input(T9_TOP_PIN) == GPIO.LOW and GPIO.input(T9_BOTTOM_PIN) == GPIO.HIGH:
                states["T9_Top"] = 1
            elif GPIO.input(T9_TOP_PIN) == GPIO.HIGH and GPIO.input(T9_BOTTOM_PIN) == GPIO.HIGH:
                states["T9_Center"] = 1

            if GPIO.input(T11_STD_PIN) == GPIO.LOW:
                states["T11_Standard"] = 1
            elif GPIO.input(T11_NVG_PIN) == GPIO.LOW:
                states["T11_NVG"] = 1
            else:
                states["T11_Off"] = 1

            buttons = [states[name] for name in VJOY_BUTTON_ORDER]
            if buttons != prev_buttons or THROTTLE != prev_throttle:
                payload = {"throttle": THROTTLE, "buttons": buttons}
                sock.sendto(json.dumps(payload).encode(), (PC_IP, PORT))
                prev_buttons = buttons.copy()
                prev_throttle = THROTTLE

            time.sleep(0.005)

    except KeyboardInterrupt:
        pass
    finally:
        encoder.stop()
        GPIO.cleanup()
        spi.close()

if __name__ == "__main__":
    main_loop()