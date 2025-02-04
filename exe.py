import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from drone import Drone
from route import RouteGenerator

# Define a central location (e.g., Washington, D.C.)
center_lat, center_lon = 38.8977, -77.0365  # White House location

# Create a RouteGenerator instance
route_gen = RouteGenerator(center_lat, center_lon, num_routes=1, waypoints_per_route=3, max_offset=0.02)

# Generate random routes
routes = route_gen.generate_routes()

# Print routes for debugging
for i, route in enumerate(routes):
    print(f"Route {i+1}: {route}")

# Initialize drones with generated routes
drones = [
   # Drone(id="1", drone_type="type1", acceleration_rate=2.0, climb_rate=3.0, speed=10.0,
    #      position_error=2.0, altitude_error=1.0, battery_consume_rate=0.05, battery_capacity=10.0, route=routes[0]),
#    Drone(id="2", drone_type="type2", acceleration_rate=2.0, climb_rate=3.0, speed=10.0,
  #        position_error=2.0, altitude_error=1.0, battery_consume_rate=0.05, battery_capacity=10.0, route=routes[1]),
    Drone(id="3", drone_type="type3", acceleration_rate=2.0, climb_rate=3.0, speed=32.0,
          position_error=2.0, altitude_error=1.0, battery_consume_rate=0.05, battery_capacity=1000.0, route=routes[0])
]

# Create a figure for 3D plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
colors = ['r', 'g', 'b']  # Different colors for each drone

# Plot waypoints
for i, route in enumerate(routes):
    latitudes = [p[0] for p in route]
    longitudes = [p[1] for p in route]
    altitudes = [p[2] for p in route]
    ax.plot(latitudes, longitudes, altitudes, 'o-', color=colors[i], label=f"Route {i+1}")

# Function to update the drone movement in real time
def update_plot():
    ax.clear()
    ax.set_xlabel("Latitude")
    ax.set_ylabel("Longitude")
    ax.set_zlabel("Altitude (m)")
    ax.set_title("Real-Time Drone Navigation")
    
    # Plot waypoints again (they remain static)
    for i, route in enumerate(routes):
        latitudes = [p[0] for p in route]
        longitudes = [p[1] for p in route]
        altitudes = [p[2] for p in route]
        ax.plot(latitudes, longitudes, altitudes, 'o-', color=colors[i], label=f"Route {i+1}")

    # Plot drones' current positions
    for i, drone in enumerate(drones):
        if drone.current_position:
            ax.scatter(*drone.current_position, color=colors[i], marker='^', s=100, label=f"Drone {drone.id}")

    ax.legend()
    plt.draw()
    plt.pause(0.1)

# Simulation loop
while any(drone.target_position for drone in drones):
    for drone in drones:
        status = drone.calculate_navigation(1)
        if status == -2:
            print(f"Drone {drone.id} battery depleted.")
        elif status == 0:
            print(f"Drone {drone.id} completed its route.")
        else:
            print(f"Drone {drone.id}: {drone.current_position}, Battery: {drone.battery_remaining:.2f} Ah, Status: {status}")
    
    update_plot()  # Update the 3D plot in real-time
    time.sleep(1)

print("Simulation completed.")
plt.show()  # Keep the final plot displayed
