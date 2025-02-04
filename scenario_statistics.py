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
    corrupted_messages = 0
    jammed_messages = 0
    spoofed_messages = 0
    delays = []
    position_errors = []

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
            if corrupted:
                corrupted_messages += 1

            # Apply Jamming effects
            if jamming and jammer:
                received_message, jammed = jammer.jam_signal(received_message)
                if jammed:
                    jammed_messages += 1
                    if received_message is None:
                        continue  # If the message is fully jammed, discard it

            # Apply Spoofing effects
            if spoofing and spoofer:
                received_message, spoofed = spoofer.spoof_message(received_message)
                if spoofed:
                    spoofed_messages += 1

            # Update GCS with the received message
            gcs.receive_update(received_message['drone_id'],
                               (received_message['latitude'],
                                received_message['longitude'],
                                received_message['altitude']))

            # Collect metrics
            delays.append(delay_ns)
            actual_position = np.array([drone.current_position[0], drone.current_position[1], drone.current_position[2]])
            received_position = np.array([received_message['latitude'], received_message['longitude'], received_message['altitude']])
            position_error = np.linalg.norm(actual_position - received_position)
            position_errors.append(position_error)

    return {
        "total_messages": total_messages,
        "corrupted_messages": corrupted_messages,
        "jammed_messages": jammed_messages,
        "spoofed_messages": spoofed_messages,
        "delays": delays,
        "position_errors": position_errors
    }

# Run simulations for each scenario and collect results
results = {}
for scenario, params in scenarios.items():
    print(f"Running scenario: {scenario}")
    result = run_simulation(**params)
    results[scenario] = result

# Plotting results
labels = list(results.keys())

# Plot Total Messages
total_msgs = [results[sc]["total_messages"] for sc in labels]
plt.figure(figsize=(10, 6))
plt.bar(labels, total_msgs, color='blue')
plt.xlabel('Scenarios')
plt.ylabel('Total Messages')
plt.title('Total Messages per Scenario')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('total_messages.png')
plt.close()

# Plot Corrupted Messages
corrupted_msgs = [results[sc]["corrupted_messages"] for sc in labels]
plt.figure(figsize=(10, 6))
plt.bar(labels, corrupted_msgs, color='red')
plt.xlabel('Scenarios')
plt.ylabel('Corrupted Messages')
plt.title('Corrupted Messages per Scenario')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/corrupted_messages.png')
plt.close()

# Plot Jammed Messages
jammed_msgs = [results[sc]["jammed_messages"] for sc in labels]
plt.figure(figsize=(10, 6))
plt.bar(labels, jammed_msgs, color='orange')
plt.xlabel('Scenarios')
plt.ylabel('Jammed Messages')
plt.title('Jammed Messages per Scenario')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/jammed_messages.png')
plt.close()

# Plot Spoofed Messages
spoofed_msgs = [results[sc]["spoofed_messages"] for sc in labels]
plt.figure(figsize=(10, 6))
plt.bar(labels, spoofed_msgs, color='green')
plt.xlabel('Scenarios')
plt.ylabel('Spoofed Messages')
plt.title('Spoofed Messages per Scenario')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/spoofed_messages.png')
plt.close()

# Plot Average Transmission Delay
avg_delays = [np.mean(results[sc]["delays"]) for sc in labels]
plt.figure(figsize=(10, 6))
plt.bar(labels, avg_delays, color='purple')
plt.xlabel('Scenarios')
plt.ylabel('Average Transmission Delay (ns)')
plt.title('Average Transmission Delay per Scenario')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/average_transmission_delay.png')
plt
#::contentReference[oaicite:0]{index=0}
 
