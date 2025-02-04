import random
import time
import numpy as np
import math

class ADSBChannel:
    def __init__(self, error_rate=0.01, frequency=1090e6, noise_figure_db=5.0):
        """
        Initialize the ADS-B channel with realistic parameters.
        :param error_rate: Probability of a message being corrupted.
        :param frequency: Carrier frequency in Hz (default is 1090 MHz for ADS-B).
        :param noise_figure_db: Receiver noise figure in dB.
        """
        self.error_rate = np.float64(error_rate)
        self.frequency = np.float64(frequency)
        self.noise_figure_db = np.float64(noise_figure_db)
        self.light_speed = np.float64(3e8)  # Speed of light in m/s

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Compute the great-circle distance (Haversine formula) between two points.
        :param lat1, lon1: Latitude and Longitude of point 1 (degrees)
        :param lat2, lon2: Latitude and Longitude of point 2 (degrees)
        :return: Distance in meters
        """
        R = np.float64(6371000)  # Earth radius in meters
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)

        a = (np.sin(delta_phi / 2) ** 2) + np.cos(phi1) * np.cos(phi2) * (np.sin(delta_lambda / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        return R * c  # Distance in meters (high precision)

    def transmit(self, message, gcs_position, tx_power_dbm=50, bandwidth_hz=1e6):
        """
        Simulate the transmission of a message through the ADS-B channel.
        :param message: The original message to be transmitted.
        :param gcs_position: (lat, lon) tuple representing the GCS position.
        :param tx_power_dbm: Transmitter power in dBm (ADS-B typically uses 51 dBm).
        :param bandwidth_hz: Bandwidth of the ADS-B signal in Hz.
        :return: The received message after channel effects.
        """
        # Extract drone and GCS positions
        drone_lat, drone_lon = message["latitude"], message["longitude"]
        gcs_lat, gcs_lon = gcs_position

        # Compute real-time distance between drone and GCS (in meters)
        distance = self.haversine_distance(drone_lat, drone_lon, gcs_lat, gcs_lon)

        # Calculate **real** propagation delay (distance / speed of light) in **nanoseconds**
        delay_seconds = distance / self.light_speed
        delay_ns = np.round(delay_seconds * 1e9, decimals=2)  # Convert to nanoseconds

        # Simulate the delay
        time.sleep(delay_seconds)  

        # Calculate signal path loss and noise effects
        path_loss_db = self.free_space_path_loss(distance)
        noise_power_dbm = self.thermal_noise_power(bandwidth_hz)

        # Received power and SNR calculation
        rx_power_dbm = tx_power_dbm - path_loss_db
        snr_db = rx_power_dbm - (noise_power_dbm + self.noise_figure_db)

        # Simulate message corruption based on SNR
        corrupted = False
        if snr_db < 0 or random.random() < self.error_rate:
            message = self.corrupt_message(message)
            corrupted = True

        return message, delay_ns, corrupted

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

    def free_space_path_loss(self, distance):
        """
        Calculate the free-space path loss for a given distance.
        :param distance: Distance between transmitter and receiver in meters.
        :return: Path loss in dB.
        """
        if distance <= 0:
            return 0  # Avoid infinite loss
        wavelength = self.light_speed / self.frequency
        path_loss_db = 20 * np.log10(4 * np.pi * distance / wavelength)
        return path_loss_db

    def thermal_noise_power(self, bandwidth_hz):
        """
        Calculate the thermal noise power for a given bandwidth.
        :param bandwidth_hz: Bandwidth in Hz.
        :return: Thermal noise power in dBm.
        """
        k = np.float64(1.38e-23)  # Boltzmann constant in J/K
        T = np.float64(290)  # Standard temperature in Kelvin
        noise_power_watts = k * T * bandwidth_hz
        noise_power_dbm = 10 * np.log10(noise_power_watts) + 30
        return noise_power_dbm
