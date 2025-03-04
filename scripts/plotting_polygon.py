import math
import numpy as np
import matplotlib.pyplot as plt

def round_to_standard_scale(value):
    """Round to standard GIS-like scale values (e.g., 500, 900, 1000)."""
    if value < 250:
        return round(value / 25) * 25  # Steps of 25 for small scales (e.g., 200, 225)
    elif value < 750:
        return round(value / 50) * 50  # Steps of 50 (e.g., 400, 450, 500)
    elif value < 1500:
        # For 875–915 → 900, etc.
        ranges = [(875, 925, 900), (925, 975, 950), (975, 1025, 1000)]
        for lower, upper, target in ranges:
            if lower <= value < upper:
                return target
        return round(value / 50) * 50  # Fallback (e.g., 850, 900)
    else:
        return round(value / 100) * 100  # Steps of 100 (e.g., 1500, 1600)

def calculate_scale(ax, fig_width_inches=25, fig_height_inches=22):
    """
    Calculate the map scale dynamically, calibrated to match GIS-like scales.
    """
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range == 0 or y_range == 0:
        return 1

    fig_width_m = fig_width_inches * 0.0254
    fig_height_m = fig_height_inches * 0.0254
    scale_x = x_range / fig_width_m
    scale_y = y_range / fig_height_m
    raw_scale = max(scale_x, scale_y)
    meters_per_cm = raw_scale * 0.01
    base_scale = meters_per_cm * 100
    calibration_factor = 3.273
    calibrated_scale = base_scale * calibration_factor
    final_scale = round_to_standard_scale(calibrated_scale)

    print(f"x_range: {x_range}, y_range: {y_range}")
    print(f"scale_x: {scale_x}, scale_y: {scale_y}, raw_scale: {raw_scale}")
    print(f"meters_per_cm: {meters_per_cm}, base_scale: {base_scale}, calibrated_scale: {calibrated_scale}")

    return final_scale

utm_coords = [
    (5, 98),
]

distances = []
for i in range(len(utm_coords) - 1):
    point1 = utm_coords[i]
    point2 = utm_coords[i+1]
    distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    distances.append(distance)

utm_x, utm_y = zip(*utm_coords)

fig, ax = plt.subplots(figsize=(25, 22))

# Calculate ranges before plotting
x_min, x_max = min(utm_x), max(utm_x)
y_min, y_max = min(utm_y), max(utm_y)
x_range = x_max - x_min
y_range = y_max - y_min

ax.plot(utm_x, utm_y, 'ko-', markersize=0, linewidth=2, label="Path (UTM)")

for i in range(len(utm_coords) - 1):
    point1 = utm_coords[i]
    point2 = utm_coords[i+1]
    mid_x = (point1[0] + point2[0]) / 2
    mid_y = (point1[1] + point2[1]) / 2
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]

    degrees = 8.50
    rotation_degrees = np.degrees(np.arctan2(dy, dx))
    rotation_degrees += -degrees if (0 <= rotation_degrees < 90) or (-180 <= rotation_degrees < -90) else degrees
    offset_pixels = 10
    offset_x_pixels = offset_pixels * math.cos(math.radians(rotation_degrees + 90))
    offset_y_pixels = offset_pixels * math.sin(math.radians(rotation_degrees + 90))
    
    ax.annotate(f"{distances[i]:.2f} m", xy=(mid_x, mid_y), xytext=(offset_x_pixels, offset_y_pixels), 
                textcoords='offset points', ha='center', va='center', rotation=rotation_degrees, 
                fontsize=15, color='black')
    
    # Add proportional offset to move text above the point
    offset_fraction = 0.005  # Adjust this value (e.g., 0.002 to 0.01) for more/less offset
    text_offset = y_range * offset_fraction
    ax.text(point1[0], point1[1] + text_offset, f"P0{i+1}", 
            horizontalalignment='center', verticalalignment='bottom', 
            rotation_mode='anchor', fontsize=15, color='black')
    ax.plot(point1[0], point1[1], "o", color='black', markersize=5, linewidth=10)

margin_factor = 0.33
x_centered_min = round(x_min - margin_factor * x_range, -1)
x_centered_max = round(x_max + margin_factor * x_range, -1)
y_centered_min = round(y_min - margin_factor * y_range, -1)
y_centered_max = round(y_max + margin_factor * y_range, -1)
ax.set_xlim(x_centered_min, x_centered_max)
ax.set_ylim(y_centered_min, y_centered_max)

custom_xticks = np.arange(x_centered_min + 30, x_centered_max - 30 + 1, 30)
custom_yticks = np.arange(y_centered_min + 30, y_centered_max - 30 + 1, 30)
ax.set_xticks(custom_xticks)
ax.set_yticks(custom_yticks)
ax.set_xticklabels([f"{int(tick)}" for tick in custom_xticks], fontsize=15)
ax.set_yticklabels([f"{int(tick)}" for tick in custom_yticks], rotation=90, fontsize=15)

ax2, ax3 = ax.twiny(), ax.twinx()
ax2.set_xlim(ax.get_xlim())
ax3.set_ylim(ax.get_ylim())
ax2.set_xticks(custom_xticks)
ax3.set_yticks(custom_yticks)
ax2.set_xticklabels([f"{int(tick)}" for tick in custom_xticks], fontsize=15)
ax3.set_yticklabels([f"{int(tick)}" for tick in custom_yticks], rotation=270, fontsize=15)

ax.grid(True, which='major', linestyle='--', linewidth=0.5)
ax2.grid(True, which='major', linestyle='--', linewidth=0.5)
ax3.grid(True, which='major', linestyle='--', linewidth=0.5)
for tick in custom_xticks: ax.axvline(x=tick, color='gray', linestyle='--', linewidth=0.75)
for tick in custom_yticks: ax.axhline(y=tick, color='gray', linestyle='--', linewidth=0.75)

dynamic_scale = calculate_scale(ax, fig_width_inches=25, fig_height_inches=22)
print(f"Scale 1:{dynamic_scale}")

plt.show()
