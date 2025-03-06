# Import required libraries for mathematical operations, numerical computations, and plotting
import math  # Provides mathematical functions (e.g., sqrt, trigonometric operations)
import numpy as np  # Enables efficient array operations and mathematical computations
import matplotlib.pyplot as plt  # Core library for creating visualizations and plots

# Define a function to round scales to GIS-standard values for practical map representation
def round_to_standard_scale(value):
    """Round to standard GIS-like scale values (e.g., 500, 900, 1000).
    
    Args:
        value (float): The raw scale value to be rounded.
    Returns:
        int: A rounded scale value aligned with GIS conventions.
    """
    if value < 250:
        # Use small increments (25 units) for finer granularity at smaller scales
        return round(value / 25) * 25  # e.g., 200, 225
    elif value < 750:
        # Increase step size to 50 units for mid-range scales
        return round(value / 50) * 50  # e.g., 400, 450, 500
    elif value < 1500:
        # Special handling for specific ranges to match common GIS scales (e.g., 900, 950, 1000)
        ranges = [(875, 925, 900), (925, 975, 950), (975, 1025, 1000)]
        for lower, upper, target in ranges:
            if lower <= value < upper:
                return target
        # Fallback to 50-unit steps if outside specific ranges
        return round(value / 50) * 50  # e.g., 850, 900
    else:
        # Use 100-unit steps for larger scales
        return round(value / 100) * 100  # e.g., 1500, 1600

# Define the core function to compute a dynamic map scale aligned with GIS standards
def calculate_scale(ax, fig_width_inches=25, fig_height_inches=22):
    """Calculate the map scale dynamically, calibrated to match GIS-like scales.
    
    Args:
        ax (matplotlib.axes.Axes): The axis object containing plot limits.
        fig_width_inches (float): Figure width in inches (default: 25).
        fig_height_inches (float): Figure height in inches (default: 22).
    Returns:
        int: The final rounded scale value (e.g., 500 for 1:500).
    """
    # Extract the current x and y limits from the axis object
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_range = x_max - x_min  # Calculate the x-axis range in data units
    y_range = y_max - y_min  # Calculate the y-axis range in data units

    # Handle edge case where there is no range (e.g., single point with no extent)
    if x_range == 0 or y_range == 0:
        return 1  # Return a default scale to avoid division by zero

    # Convert figure dimensions from inches to meters (1 inch = 0.0254 meters)
    fig_width_m = fig_width_inches * 0.0254
    fig_height_m = fig_height_inches * 0.0254
    # Compute raw scales as data units per meter for x and y directions
    scale_x = x_range / fig_width_m
    scale_y = y_range / fig_height_m
    # Use the larger scale to ensure the map fits within the figure consistently
    raw_scale = max(scale_x, scale_y)
    # Convert to meters per centimeter for practical scale interpretation
    meters_per_cm = raw_scale * 0.01
    base_scale = meters_per_cm * 100  # Scale to a base unit for calibration
    calibration_factor = 3.273  # Empirical factor to align with GIS standards
    calibrated_scale = base_scale * calibration_factor  # Apply calibration
    final_scale = round_to_standard_scale(calibrated_scale)  # Round to standard value

    # Print intermediate values for debugging and verification
    print(f"x_range: {x_range}, y_range: {y_range}")
    print(f"scale_x: {scale_x}, scale_y: {scale_y}, raw_scale: {raw_scale}")
    print(f"meters_per_cm: {meters_per_cm}, base_scale: {base_scale}, calibrated_scale: {calibrated_scale}")

    return final_scale

# Define sample UTM coordinates as a list of tuples (x, y)
# Currently a single point, but expandable for multiple points
utm_coords = [
    (5, 98),
]

# Calculate Euclidean distances between consecutive points
distances = []
for i in range(len(utm_coords) - 1):
    point1 = utm_coords[i]
    point2 = utm_coords[i+1]
    # Use the Pythagorean theorem to compute distance between points
    distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    distances.append(distance)  # Store distances (empty with one point)

# Unzip UTM coordinates into separate x and y lists for plotting
utm_x, utm_y = zip(*utm_coords)

# Initialize the figure and axis with predefined dimensions for consistent output
fig, ax = plt.subplots(figsize=(25, 22))  # 25x22 inches mimics a standard map size

# Determine the data range for setting plot limits
x_min, x_max = min(utm_x), max(utm_x)
y_min, y_max = min(utm_y), max(utm_y)
x_range = x_max - x_min  # Range of x coordinates
y_range = y_max - y_min  # Range of y coordinates

# Plot the UTM path as a black line with markers
# 'ko-' specifies black color (k), circle markers (o), and solid line (-)
ax.plot(utm_x, utm_y, 'ko-', markersize=0, linewidth=2, label="Path (UTM)")

# Annotate distances and label points (inactive with a single point)
for i in range(len(utm_coords) - 1):
    point1 = utm_coords[i]
    point2 = utm_coords[i+1]
    # Calculate midpoint for distance annotation placement
    mid_x = (point1[0] + point2[0]) / 2
    mid_y = (point1[1] + point2[1]) / 2
    dx = point2[0] - point1[0]  # Delta x for angle calculation
    dy = point2[1] - point1[1]  # Delta y for angle calculation

    degrees = 8.50  # Fixed adjustment for label alignment readability
    # Calculate the angle of the line segment in degrees
    rotation_degrees = np.degrees(np.arctan2(dy, dx))
    # Adjust rotation for better visual alignment based on quadrant
    rotation_degrees += -degrees if (0 <= rotation_degrees < 90) or (-180 <= rotation_degrees < -90) else degrees
    offset_pixels = 10  # Offset distance for text placement
    # Convert rotation to offset coordinates for annotation
    offset_x_pixels = offset_pixels * math.cos(math.radians(rotation_degrees + 90))
    offset_y_pixels = offset_pixels * math.sin(math.radians(rotation_degrees + 90))
    
    # Add distance annotation between points with formatted text
    ax.annotate(f"{distances[i]:.2f} m", xy=(mid_x, mid_y), xytext=(offset_x_pixels, offset_y_pixels), 
                textcoords='offset points', ha='center', va='center', rotation=rotation_degrees, 
                fontsize=15, color='black')
    
    # Label each point with a proportional offset above it
    offset_fraction = 0.005  # Fraction of y-range for consistent text offset
    text_offset = y_range * offset_fraction
    ax.text(point1[0], point1[1] + text_offset, f"P0{i+1}", 
            horizontalalignment='center', verticalalignment='bottom', 
            rotation_mode='anchor', fontsize=15, color='black')
    # Plot point marker explicitly (redundant here due to initial plot)
    ax.plot(point1[0], point1[1], "o", color='black', markersize=5, linewidth=10)

# Apply margins to center the plot and round limits for cleaner visualization
margin_factor = 0.33  # Proportion of range to add as margin
x_centered_min = round(x_min - margin_factor * x_range, -1)  # Round to nearest 10
x_centered_max = round(x_max + margin_factor * x_range, -1)
y_centered_min = round(y_min - margin_factor * y_range, -1)
y_centered_max = round(y_max + margin_factor * y_range, -1)
ax.set_xlim(x_centered_min, x_centered_max)  # Set x-axis limits
ax.set_ylim(y_centered_min, y_centered_max)  # Set y-axis limits

# Define custom tick marks for consistent and readable intervals
custom_xticks = np.arange(x_centered_min + 30, x_centered_max - 30 + 1, 30)  # Step by 30 units
custom_yticks = np.arange(y_centered_min + 30, y_centered_max - 30 + 1, 30)
ax.set_xticks(custom_xticks)  # Apply x-axis ticks
ax.set_yticks(custom_yticks)  # Apply y-axis ticks
# Set tick labels with integer formatting for clarity
ax.set_xticklabels([f"{int(tick)}" for tick in custom_xticks], fontsize=15)
ax.set_yticklabels([f"{int(tick)}" for tick in custom_yticks], rotation=90, fontsize=15)

# Add secondary axes to display tick labels on top and right for map-like presentation
ax2, ax3 = ax.twiny(), ax.twinx()  # Create twin axes for top (x) and right (y)
ax2.set_xlim(ax.get_xlim())  # Match limits to primary x-axis
ax3.set_ylim(ax.get_ylim())  # Match limits to primary y-axis
ax2.set_xticks(custom_xticks)  # Set top ticks
ax3.set_yticks(custom_yticks)  # Set right ticks
ax2.set_xticklabels([f"{int(tick)}" for tick in custom_xticks], fontsize=15)
ax3.set_yticklabels([f"{int(tick)}" for tick in custom_yticks], rotation=270, fontsize=15)

# Add gridlines to enhance readability and provide a reference grid
ax.grid(True, which='major', linestyle='--', linewidth=0.5)  # Primary grid
ax2.grid(True, which='major', linestyle='--', linewidth=0.5)  # Top grid
ax3.grid(True, which='major', linestyle='--', linewidth=0.5)  # Right grid
# Add vertical and horizontal lines at tick positions for emphasis
for tick in custom_xticks: 
    ax.axvline(x=tick, color='gray', linestyle='--', linewidth=0.75)
for tick in custom_yticks: 
    ax.axhline(y=tick, color='gray', linestyle='--', linewidth=0.75)

# Compute the dynamic map scale based on current plot limits and figure size
dynamic_scale = calculate_scale(ax, fig_width_inches=25, fig_height_inches=22)
# Display the computed scale in a standard format
print(f"Scale 1:{dynamic_scale}")

# Render and display the final plot
plt.show()
