class DeviceState:
    IDLE = 2
    BUSY = 4
    RECOGNIZING = 8
    EXPECTING_SPEECH = 16

    def __init__(self):
        self.current_state = DeviceState.IDLE


    def set_state(self, state):
        self.current_state = state


    def get_state(self):
        print(("[STATE:DEVICE_STATE] device status (%s)" % (self.current_state)))
        return self.current_state
