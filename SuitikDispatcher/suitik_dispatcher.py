from evdev import InputDevice, list_devices, ecodes, categorize

devices = [InputDevice(path) for path in list_devices()]

rfid_reader = None

for dev in devices:
    if dev.name.lower().endswith("ic reader"):
        print("device found")
        print(dev)
        rfid_reader = dev
        break

with rfid_reader.grab_context():
    for event in rfid_reader.read_loop():
        if event.type == ecodes.EV_KEY:
            print(event)
            print(categorize(event))
