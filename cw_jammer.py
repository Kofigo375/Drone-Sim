import random
import time

class ContinuousWaveJammer:
    """
    This class simulates a continuous wave (CW) jamming mechanism.
    CW jamming transmits a constant carrier signal intended to overpower or obstruct legitimate signals.
    """
    def __init__(self, jamming_probability=0.5, noise_intensity=0.7, jamming_power_dbm=-70):
        """
        :param jamming_probability: Probability of blocking each message entirely.
        :param noise_intensity: Intensity of the noise (not used in CW jamming but kept for compatibility).
        :param jamming_power_dbm: Power level of the jamming signal (in dBm).
        """
        self.jamming_probability = jamming_probability
        self.noise_intensity = noise_intensity  # Kept for compatibility
        self.jamming_power_dbm = jamming_power_dbm

    def jam_signal(self, message):
        """
        A continuous wave jammer typically blocks the signal completely if jamming occurs.
        """
        if random.random() < self.jamming_probability:
            print("[CW Jammer] Jamming message:", message)
            # In a continuous wave scenario, we assume the message is fully lost.
            return None, True
        return message, False

    def jamming_signal_power(self):
        """
        Returns the power of the CW jamming signal in dBm.
        """
        return self.jamming_power_dbm