import math
import random
import time

class DirectionalJammer:
    """
    Simulates a directional (beamforming) jammer, focusing jamming power within a narrow angle 
    aiming at a specified target location. Drones or GCS within the beam have an increased 
    probability of being jammed.
    """
    def __init__(
        self,
        target_position,
        beam_width_degrees=30,
        jamming_probability=0.3,
        noise_intensity=0.7,
        jamming_power_dbm=-70
    ):
        """
        :param target_position: (lat, lon) coordinates of the jammer's main beam aim point.
        :param beam_width_degrees: Angular width of the beam in degrees.
        :param jamming_probability: Base probability of blocking messages.
        :param noise_intensity: For partial message corruption vs total loss.
        :param jamming_power_dbm: Power level of the jamming signal (in dBm).
        """
        self.target_position = target_position
        self.beam_width_degrees = beam_width_degrees
        self.jamming_probability = jamming_probability
        self.noise_intensity = noise_intensity
        self.jamming_power_dbm = jamming_power_dbm

    def jam_signal(self, message):
        """
        Increases jamming probability if the message’s position is within the beam width.
        """
        lat, lon = message.get('latitude'), message.get('longitude')
        if lat is None or lon is None:
            return message, False

        adjusted_probability = self._calculate_beam_probability(lat, lon)
        if random.random() < adjusted_probability:
            print("[DirectionalJammer] Jamming active, target within beam range.")
            if random.random() < self.noise_intensity:
                print("[DirectionalJammer] Message completely lost!")
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

    def _calculate_beam_probability(self, lat, lon):
        """
        Determines if the (lat, lon) is within the jammer's main beam.
        If so, increases the jamming_probability; otherwise, returns the base probability.
        """
        angle_diff = self._angular_difference(self.target_position, (lat, lon))
        half_beam = self.beam_width_degrees / 2
        if abs(angle_diff) <= half_beam:
            return min(1.0, self.jamming_probability * 2)
        return self.jamming_probability

    def _angular_difference(self, pos1, pos2):
        """
        Calculates approximate bearing difference between two lat/lon positions (in degrees).
        """
        lat1, lon1 = map(math.radians, pos1)
        lat2, lon2 = map(math.radians, pos2)

        d_lon = lon2 - lon1
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        bearing = math.degrees(math.atan2(y, x))
        return bearing