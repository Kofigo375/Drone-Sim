import random
import time

class SweepingJammer:
    """
    This class simulates a frequency-hopping jammer. It randomly hops between
    specified frequencies at given intervals, causing partial or total message loss.
    """
    def __init__(
        self,
        jamming_probability=0.3,
        noise_intensity=0.7,
        jamming_power_dbm=-70,
        hop_interval=2.0,
        frequency_list=None
    ):
        """
        :param jamming_probability: Probability of blocking each message entirely.
        :param noise_intensity: Intensity for partial message corruption.
        :param jamming_power_dbm: Power level of the jamming signal (in dBm).
        :param hop_interval: Time in seconds between frequency hops.
        :param frequency_list: List of possible frequencies for the jammer to hop through.
        """
        self.jamming_probability = jamming_probability
        self.noise_intensity = noise_intensity
        self.jamming_power_dbm = jamming_power_dbm
        self.hop_interval = hop_interval
        self.frequency_list = frequency_list or [907e6, 915e6, 920e6, 925e6]
        self.current_frequency = random.choice(self.frequency_list)
        self.last_hop_time = time.time()

    def jam_signal(self, message):
        """
        Introduce signal degradation or block messages entirely.
        Frequency hopping is triggered if hop_interval has elapsed.
        """
        self._maybe_hop_frequency()

        if random.random() < self.jamming_probability:
            print(f"[SweepingJammer] Jamming on frequency {self.current_frequency}")
            if random.random() < self.noise_intensity:
                print("[SweepingJammer] Message completely lost!")
                return None, True
            else:
                message['latitude'] += random.uniform(-0.1, 0.1)
                message['longitude'] += random.uniform(-0.1, 0.1)
                message['altitude'] += random.uniform(-100, 100)
                return message, True
        return message, False

    def jamming_signal_power(self):
        """Returns the power of the jamming signal in dBm."""
        return self.jamming_power_dbm

    def _maybe_hop_frequency(self):
        """
        Switches to a different frequency if the hop interval has elapsed.
        """
        current_time = time.time()
        if (current_time - self.last_hop_time) >= self.hop_interval:
            self.current_frequency = random.choice(self.frequency_list)
            self.last_hop_time = current_time
            print(f"[SweepingJammer] Frequency hopped to {self.current_frequency} Hz")