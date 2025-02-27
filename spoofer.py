import random
import numpy as np
import time    
    
class Spoofer:
    def __init__(self, spoof_probability=0.3, fake_drone_id="FAKE123"):
        self.spoof_probability = spoof_probability
        self.fake_drone_id = fake_drone_id
        
        # Track incremental offsets so they grow with each spoofed message
        self.lat_offset = 0.0
        self.lon_offset = 0.0
        self.alt_offset = 0.0
        
        # Define small increments
        self.lat_step = 0.001
        self.lon_step = 0.001
        self.alt_step = 1.0

    def spoof_message(self, message):
        # Only spoof some fraction of messages
        if random.random() < self.spoof_probability:
            # Increase offsets gradually
            self.lat_offset += self.lat_step
            self.lon_offset += self.lon_step
            self.alt_offset += self.alt_step

            # Copy original message
            spoofed_message = message.copy()

            # Gradually shift the coordinates
            spoofed_message['latitude'] += self.lat_offset
            spoofed_message['longitude'] += self.lon_offset
            spoofed_message['altitude'] += self.alt_offset

            # Optionally mask drone ID
            if random.random() < 0.5:
                spoofed_message['drone_id'] = self.fake_drone_id

            return spoofed_message, True

        return message, False