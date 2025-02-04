import time
import numpy as np
import matplotlib.pyplot as plt
from drone import Drone
from route import RouteGenerator
from gcs import GCS
from adsbchannel import ADSBChannel
from jammer import Jammer
from spoofer import Spoofer

# Define central location (e.g., Washington, D.C.)
center_lat, center_lon = 38.8977, -77.0365  # White House location

# Initialize GCS
gcs = GCS(center_lat, center_lon)
gcs_pos = (center_lat, center_lon)

# Create a RouteGenerator instance
route_gen = RouteGenerator(center_lat, center_lon, num_routes=1, waypoints_per_route=5, max_offset=0.02)
routes = route_gen.generate_routes()

# Function to initialize drones
def initialize_drones():
    return [
        Drone(id=f"{i+1}", drone_type=f"type{i+1}", acceleration_rate=2.0, climb_rate=3.0, speed=10.0 + i*5,
              position_error=2.0, altitude_error=1.0, battery_consume_rate=0.05, battery_capacity=10.0 + i*5, route=routes[i])
        for i in range(len(routes))
    ]

# Simulation scenarios
scenarios = {
    "No Attacks": {"jamming": False, "spoofing": False},
    "Only Spoofing": {"jamming": False, "spoofing": True},
    "Only Jamming": {"jamming": True, "spoofing": False},
    "Jamming and Spoofing": {"jamming": True, "spoofing": True},
    "Aggressive Spoofing": {"jamming": False, "spoofing": True, "spoof_probability": 0.7}
}

# Function to run a simulation scenario
def run_simulation(jamming=False, spoofing=False, spoof_probability=0.3):
    # Initialize the communication channel, jammer, and spoofer
    channel = ADSBChannel()
    jammer = Jammer(jamming_probability=0.4, noise_intensity=0.8) if jamming else None
    spoofer = Spoofer(spoof_probability=spoof_probability, fake_drone_id="FAKE-DRONE") if spoofing else None

    # Initialize drones for this simulation
    drones = initialize_drones()

    # Data collection
    total_messages = 0
    lost_messages = 0
    packet_loss_over_time = []

    for drone in drones:
        while True:
            status = drone.calculate_navigation(1)
            if status in [-1, -2, 0]:
                break

            # Original (ideal) message
            original_message = {
                'drone_id': drone.id,
                'latitude': drone.current_position[0],
                'longitude': drone.current_position[1],
                'altitude': drone.current_position[2],
                'timestamp': time.time()
            }

            # Simulate transmission from the drone to the GCS
            received_message, delay_ns, corrupted = channel.transmit(original_message, gcs_pos)
            total_messages += 1

            # Apply Jamming effects
            if jamming and jammer:
                received_message, jammed = jammer.jam_signal(received_message)
                if jammed and received_message is None:
                    lost_messages += 1
                    packet_loss_over_time.append((total_messages, lost_messages / total_messages * 100))
                    continue  # If the message is fully jammed, discard it

            # Apply Spoofing effects
            if spoofing and spoofer:
                received_message, spoofed = spoofer.spoof_message(received_message)

            # Update GCS with the received message
            gcs.receive_update(received_message['drone_id'],
                               (received_message['latitude'],
                                received_message['longitude'],
                                received_message['altitude']))

            # If the message was corrupted and not jammed, consider it lost
            if corrupted and not (jamming and jammed):
                lost_messages += 1

            # Record packet loss percentage over time
            packet_loss_over_time.append((total_messages, lost_messages / total_messages * 100))

    return packet_loss_over_time

# Run simulations for each scenario and collect results
results = {}
for scenario, params in scenarios.items():
    print(f"Running scenario: {scenario}")
    packet_loss_data = run_simulation(**params)
    results[scenario] = packet_loss_data

# Plotting packet loss over time for each scenario
plt.figure(figsize=(12, 8))
colors = ['blue', 'green', 'orange', 'red', 'purple']

for (scenario, data), color in zip(results.items(), colors):
    times, packet_loss = zip(*data)
    plt.plot(times, packet_loss, label=scenario, color=color)

plt.xlabel('Total Messages Sent')
plt.ylabel('Packet Loss (%)')
plt.title('Packet Loss over Simulation Time for Different Scenarios')
plt.legend()
plt.grid(True)
plt.show()
plt.savefig('results/packet_loss.png')

