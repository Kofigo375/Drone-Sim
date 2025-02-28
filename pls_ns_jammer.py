import random
import time

class PulsedNoiseJammer:
    """
    Simulates a pulsed noise (burst) jammer by emitting short, high-intensity pulses
    at random intervals, causing sporadic disruption in communications.
    """
    def __init__(
        self,
        jamming_probability=0.3,
        noise_intensity=0.9,
        jamming_power_dbm=-60,
        pulse_interval_range=(1.0, 3.0),
        pulse_duration=0.5
    ):
        """
        :param jamming_probability: Probability of blocking each message entirely.
        :param noise_intensity: Controls chance of partial corruption vs total loss.
        :param jamming_power_dbm: Power level of the jamming signal in dBm.
        :param pulse_interval_range: (min, max) seconds between pulses.
        :param pulse_duration: Duration in seconds of each noise pulse.
        """
        self.jamming_probability = jamming_probability
        self.noise_intensity = noise_intensity
        self.jamming_power_dbm = jamming_power_dbm
        # Define the range for random intervals between noise pulses
        self.pulse_interval_min, self.pulse_interval_max = pulse_interval_range
        self.pulse_duration = pulse_duration
        self.next_pulse_time = time.time() + random.uniform(*pulse_interval_range)
        self.pulse_active_until = None

    def jam_signal(self, message):
        """
        If we are within a pulse, significantly increase jamming probability.
        If a pulse should start, schedule the end of the pulse and the next one.
        """
        current_time = time.time()
        self._update_pulse_status(current_time)

        # If currently in a pulse, apply higher jamming probability
        effective_jamming_probability = self.jamming_probability
        if self.is_pulse_active(current_time):
            effective_jamming_probability = min(1.0, self.jamming_probability + 0.5)

        if random.random() < effective_jamming_probability:
            print(f"[PulsedNoiseJammer] Pulsed jamming active. Noise intensity: {self.noise_intensity}")
            if random.random() < self.noise_intensity:
                print("[PulsedNoiseJammer] Message completely lost!")
                return None, True
            else:
                message['latitude'] += random.uniform(-0.05, 0.05)
                message['longitude'] += random.uniform(-0.05, 0.05)
                message['altitude'] += random.uniform(-50, 50)
                return message, True
        return message, False

    def jamming_signal_power(self):
        """Returns the power of the jamming signal in dBm."""
        return self.jamming_power_dbm

    def is_pulse_active(self, current_time):
        """Check if we're currently within a pulse window."""
        return self.pulse_active_until is not None and current_time <= self.pulse_active_until

    def _update_pulse_status(self, current_time):
        """
        Starts a new pulse if we've reached the next pulse time.
        Ends the pulse when its duration is complete.
        Reschedules the next pulse once the current one ends.
        """
        # Start a new pulse
        if current_time >= self.next_pulse_time and not self.is_pulse_active(current_time):
            self.pulse_active_until = current_time + self.pulse_duration

        # If pulse just ended, schedule the next pulse
        if self.pulse_active_until and current_time > self.pulse_active_until:
            self.next_pulse_time = current_time + random.uniform(self.pulse_interval_min, self.pulse_interval_max)
            self.pulse_active_until = None