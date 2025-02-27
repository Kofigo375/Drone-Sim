import random
import time
import numpy as np

class Channel:
    def __init__(self, delay_mean=0.1, delay_std=0.05, error_rate=0.01, frequency=1090e6, noise_figure_db=5.0):
        """
        Initialize the channel with specified parameters.
        :param delay_mean: Mean of the transmission delay in seconds.
        :param delay_std: Standard deviation of the transmission delay.
        :param error_rate: Probability of a message being corrupted.
        :param frequency: Frequency of the signal in Hz.
        :param noise_figure_db: Noise figure of the receiver in dB.
        """
        self.delay_mean = delay_mean
        self.delay_std = delay_std
        self.error_rate = error_rate
        self.frequency = frequency
        self.noise_figure_db = noise_figure_db
        self.light_speed = 3e8  # Speed of light in m/s

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)

        a = (np.sin(delta_phi / 2) ** 2) + np.cos(phi1) * np.cos(phi2) * (np.sin(delta_lambda / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        return R * c  # Distance in meters

    def free_space_path_loss(self, distance):
        if distance <= 0:
            return 0  # Avoid infinite loss
        wavelength = self.light_speed / self.frequency
        path_loss_db = 20 * np.log10(4 * np.pi * distance / wavelength)
        return path_loss_db

    def thermal_noise_power(self, bandwidth_hz):
        k = 1.38e-23  # Boltzmann constant in J/K
        T = 290  # Standard temperature in Kelvin
        noise_power_watts = k * T * bandwidth_hz
        noise_power_dbm = 10 * np.log10(noise_power_watts) + 30
        return noise_power_dbm

    def transmit(self, message, gcs_position, tx_power_dbm=50, bandwidth_hz=1e6):
        """
        Simulate the transmission of a message through the channel.
        :param message: The original message to be transmitted.
        :param gcs_position: The position of the ground control station (latitude, longitude).
        :param tx_power_dbm: Transmission power in dBm.
        :param bandwidth_hz: Bandwidth of the signal in Hz.
        :return: The received message after channel effects.
        """
        drone_lat, drone_lon = message["latitude"], message["longitude"]
        gcs_lat, gcs_lon = gcs_position

        # Calculate distance and delay
        distance = self.haversine_distance(drone_lat, drone_lon, gcs_lat, gcs_lon)
        delay_seconds = distance / self.light_speed
        delay_ns = np.round(delay_seconds * 1e9, decimals=2)
        time.sleep(delay_seconds)

        # Calculate path loss and noise power
        path_loss_db = self.free_space_path_loss(distance)
        noise_power_dbm = self.thermal_noise_power(bandwidth_hz)

        # Calculate received power and SNR
        rx_power_dbm = tx_power_dbm - path_loss_db
        snr_db = rx_power_dbm - (noise_power_dbm + self.noise_figure_db)

        # Simulate message corruption based on SNR and error rate
        corrupted = False
        if snr_db < 0 or random.random() < self.error_rate:
            message = self.corrupt_message(message)
            corrupted = True

        return message, delay_ns, corrupted, snr_db

    def corrupt_message(self, message):
        """
        Simulate corruption of the message.
        :param message: The original message.
        :return: A corrupted version of the message.
        """
        corrupted_message = message.copy()
        # Introduce random errors into the position data
        corrupted_message['latitude'] += random.uniform(-0.01, 0.01)
        corrupted_message['longitude'] += random.uniform(-0.01, 0.01)
        corrupted_message['altitude'] += random.uniform(-10, 10)
        return corrupted_message
