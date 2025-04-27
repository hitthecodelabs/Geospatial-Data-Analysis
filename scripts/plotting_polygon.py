import math
import numpy as np
import matplotlib.pyplot as plt

# Assume utm_coords is defined before this script runs
# Example placeholder:
# utm_coords = [(500000, 4500000), (500100, 4500050), (500150, 4500150), (500050, 4500200)] 

def round_to_standard_scale(value):
    """Round to standard GIS-like scale values (e.g., 500, 900, 1000)."""
    if value <= 0: return 1 # Handle zero or negative input
    if value < 250:
        return max(25, round(value / 25) * 25)  # Steps of 25, min 25
    elif value < 750:
        return round(value / 50) * 50  # Steps of 50 (e.g., 400, 450, 500)
    elif value < 1500:
        # For 875–915 → 900, etc.
        ranges = [(875, 925, 900), (925, 975, 950), (975, 1025, 1000)]
        for lower, upper, target in ranges:
            if lower <= value < upper:
                return target
        # Ensure rounding doesn't go below 750 inappropriately
        rounded_val = round(value / 50) * 50
        return max(750, rounded_val) # Fallback (e.g., 750, 800, 850,...)
    else:
         # Ensure rounding doesn't go below 1500 inappropriately
        rounded_val = round(value / 100) * 100
        return max(1500, rounded_val) # Steps of 100 (e.g., 1500, 1600)


def calculate_scale(ax, fig_width_inches=25, fig_height_inches=22):
    """
    Calculate the map scale dynamically, calibrated to match GIS-like scales.
    """
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range <= 0 or y_range <= 0: # Use <= to handle single point plots
        print("Warning: Zero or negative data range detected. Scale calculation might be inaccurate.")
        # Try to estimate based on figure size if data range is zero
        # This is a rough fallback - scale is less meaningful here
        if x_range <= 0 and y_range <= 0: return 1 # No range at all
        # If one range is zero, base scale on the other dimension relative to figure size
        fig_width_m = fig_width_inches * 0.0254
        fig_height_m = fig_height_inches * 0.0254
        if x_range > 0: # Only x has range
            raw_scale = x_range / fig_width_m
        else: # Only y has range (or both zero handled above)
             raw_scale = y_range / fig_height_m
    else:
        fig_width_m = fig_width_inches * 0.0254
        fig_height_m = fig_height_inches * 0.0254
        scale_x = x_range / fig_width_m
        scale_y = y_range / fig_height_m
        raw_scale = max(scale_x, scale_y) # Ensure everything fits

    if raw_scale <= 0: # Catch potential issues leading to non-positive scale
         print("Warning: Non-positive raw scale calculated. Defaulting scale.")
         return 1000 # Or some other default

    # --- Continue Calculation ---
    meters_per_cm = raw_scale * 0.01
    base_scale = meters_per_cm * 100 # Should be same as raw_scale mathematically
    calibration_factor = 3.273
    calibrated_scale = base_scale * calibration_factor
    final_scale = round_to_standard_scale(calibrated_scale)

    print(f"x_range: {x_range:.2f}, y_range: {y_range:.2f}")
    print(f"scale_x: {scale_x:.2f}, scale_y: {scale_y:.2f}, raw_scale: {raw_scale:.2f}")
    print(f"meters_per_cm: {meters_per_cm:.2f}, base_scale: {base_scale:.2f}, calibrated_scale: {calibrated_scale:.2f}")

    return final_scale

# --- Data Preparation ---
# This part requires utm_coords to be defined beforehand
if 'utm_coords' not in locals() or not isinstance(utm_coords, (list, tuple)) or len(utm_coords) < 2:
     print("Error: 'utm_coords' is not defined or is invalid. Using dummy data.")
     utm_coords = [(500000, 4500000), (500100, 4500050), (500150, 4500150), (500050, 4500200), (500000, 4500100)]

distances = []
for i in range(len(utm_coords) - 1):
    point1 = utm_coords[i]
    point2 = utm_coords[i+1]
    # Check if points are valid tuples/lists of numbers
    if not (isinstance(point1, (list, tuple)) and len(point1) == 2 and all(isinstance(c, (int, float)) for c in point1) and
            isinstance(point2, (list, tuple)) and len(point2) == 2 and all(isinstance(c, (int, float)) for c in point2)):
        print(f"Warning: Invalid coordinate format at index {i}. Skipping distance calculation.")
        distances.append(float('nan')) # Append NaN for invalid segment
        continue
    distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    distances.append(distance)

# Check if utm_coords is empty after potential errors
if not utm_coords:
     print("Error: No valid coordinates to plot.")
     exit()

# Unpack coordinates - handle case of single point
if len(utm_coords) > 0:
    utm_x, utm_y = zip(*utm_coords)
else:
    utm_x, utm_y = [], []

# --- Plotting Setup ---
fig, ax = plt.subplots(figsize=(25, 22))

# Calculate ranges before plotting (used later for offsets and limits)
if utm_x and utm_y: # Ensure there's data
    x_min, x_max = min(utm_x), max(utm_x)
    y_min, y_max = min(utm_y), max(utm_y)
    # Handle case where all points are the same
    x_range = x_max - x_min if x_max > x_min else 1.0 # Avoid zero range
    y_range = y_max - y_min if y_max > y_min else 1.0 # Avoid zero range
else: # No data or single point default
    x_min, x_max, x_range = 0, 1, 1
    y_min, y_max, y_range = 0, 1, 1


# Plot path only if there are multiple points
if len(utm_coords) > 1:
    ax.plot(utm_x, utm_y, 'k-', linewidth=2, label="Path (UTM)") # Removed 'o' marker, added explicitly later
elif len(utm_coords) == 1:
     ax.plot(utm_x[0], utm_y[0], 'ko', markersize=5) # Plot single point if only one

# --- Annotation Loop ---
for i in range(len(utm_coords) - 1):
    point1 = utm_coords[i]
    point2 = utm_coords[i+1]

    # Check again for valid points before processing segment
    if not (isinstance(point1, (list, tuple)) and len(point1) == 2 and all(isinstance(c, (int, float)) for c in point1) and
            isinstance(point2, (list, tuple)) and len(point2) == 2 and all(isinstance(c, (int, float)) for c in point2)):
        continue # Skip annotation for invalid segment

    mid_x = (point1[0] + point2[0]) / 2
    mid_y = (point1[1] + point2[1]) / 2
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]

    # Avoid calculations if segment length is zero
    if dx == 0 and dy == 0:
        rotation_degrees = 0
        # Optionally add a marker for coincident points if desired
    else:
        rotation_degrees = np.degrees(np.arctan2(dy, dx))

    # --- Distance Annotation ---
    if i < len(distances) and not math.isnan(distances[i]): # Check if distance is valid
        degrees = 8.50
        display_rotation = rotation_degrees
        # Adjust rotation offset based on quadrant
        display_rotation += -degrees if (0 <= rotation_degrees < 90) or (-180 <= rotation_degrees < -90) else degrees

        offset_pixels = 10
        # Calculate offset perpendicular to the *adjusted* angle for placement
        offset_angle_rad = math.radians(display_rotation + 90)
        offset_x_pixels = offset_pixels * math.cos(offset_angle_rad)
        offset_y_pixels = offset_pixels * math.sin(offset_angle_rad)

        ax.annotate(f"{distances[i]:.2f} m", xy=(mid_x, mid_y), xytext=(offset_x_pixels, offset_y_pixels),
                    textcoords='offset points', ha='center', va='center', rotation=display_rotation,
                    fontsize=15, color='black')

    # --- Point Label and Marker ---
    offset_fraction = 0.005
    # Use dynamic range from axes if available, otherwise calculated range
    try:
        current_y_limits = ax.get_ylim()
        plot_y_range = current_y_limits[1] - current_y_limits[0]
    except:
        plot_y_range = y_range # Fallback to calculated range

    text_offset = plot_y_range * offset_fraction if plot_y_range > 0 else 5 # Use fixed offset if range is zero

    # Add label for the start point of the segment
    # if i+2!=len(utm_coords):
    if i<10:
        ax.text(point1[0], point1[1] + text_offset, f"P0{i+1}",
                horizontalalignment='center', verticalalignment='bottom',
                rotation_mode='anchor', fontsize=15, color='black')
    else:
        ax.text(point1[0], point1[1] + text_offset, f"P{i+1}",
                horizontalalignment='center', verticalalignment='bottom',
                rotation_mode='anchor', fontsize=15, color='black')
    # Add marker for the start point
    ax.plot(point1[0], point1[1], "o", color='black', markersize=5)

# # Add label and marker for the very last point
# if len(utm_coords) > 0:
#     last_point = utm_coords[-1]
#     if isinstance(last_point, (list, tuple)) and len(last_point) == 2 and all(isinstance(c, (int, float)) for c in last_point):
#         try:
#             current_y_limits = ax.get_ylim()
#             plot_y_range = current_y_limits[1] - current_y_limits[0]
#         except:
#             plot_y_range = y_range
#         text_offset = plot_y_range * offset_fraction if plot_y_range > 0 else 5

#         ax.text(last_point[0], last_point[1] + text_offset, f"P0{len(utm_coords)}",
#                 horizontalalignment='center', verticalalignment='bottom',
#                 rotation_mode='anchor', fontsize=15, color='black')
#         ax.plot(last_point[0], last_point[1], "o", color='black', markersize=5)


# --- Set Axis Limits with Margins ---
margin_factor = 0.33
# Ensure ranges are positive for margin calculation
x_range_for_margin = max(x_range, 1.0) # Use at least 1.0 to avoid zero margin
y_range_for_margin = max(y_range, 1.0)

x_margin = margin_factor * x_range_for_margin
y_margin = margin_factor * y_range_for_margin

x_centered_min = round(x_min - x_margin, -1) # Round to nearest 10
x_centered_max = round(x_max + x_margin, -1) # Round to nearest 10
y_centered_min = round(y_min - y_margin, -1) # Round to nearest 10
y_centered_max = round(y_max + y_margin, -1) # Round to nearest 10

# Prevent limits from collapsing if range was very small
if x_centered_max <= x_centered_min: x_centered_max = x_centered_min + 10
if y_centered_max <= y_centered_min: y_centered_max = y_centered_min + 10


ax.set_xlim(x_centered_min, x_centered_max)
ax.set_ylim(y_centered_min, y_centered_max)


# --- Get Final Corner Coordinates (for info) ---
x_limits = ax.get_xlim()
y_limits = ax.get_ylim()
bottom_left = (x_limits[0], y_limits[0])
bottom_right = (x_limits[1], y_limits[0])
top_left = (x_limits[0], y_limits[1])
top_right = (x_limits[1], y_limits[1])

print("--- Final Plot Area Corners ---")
print("Bottom Left:", bottom_left)
print("Bottom Right:", bottom_right)
print("Top Left:", top_left)
print("Top Right:", top_right)
print()

# --- Enhanced Tick Generation ---
tick_margin_factor = 0.0 # Margin from edges for tick calculation range (can be > 0)
num_ticks = 5          # Fixed number of ticks for both axes
tick_rounding_base = 10 # Round tick steps to nearest 10
max_adjustments = 5    # Limit the number of shifts in adjustment loops

# --- X-axis Ticks ---
print("--- X-Tick Calculation ---")
x_axis_range = x_limits[1] - x_limits[0]
x_tick_min = x_limits[0] + tick_margin_factor * x_axis_range
x_tick_max = x_limits[1] - tick_margin_factor * x_axis_range
x_tick_calc_range = x_tick_max - x_tick_min

if x_tick_calc_range > 0 and num_ticks > 1:
    # Generate initial xticks
    initial_xticks = np.linspace(x_tick_min, x_tick_max, num_ticks)
    tick_diffs = np.diff(initial_xticks)
    avg_tick_diff = round(np.mean(tick_diffs) / tick_rounding_base) * tick_rounding_base
    if avg_tick_diff == 0: avg_tick_diff = tick_rounding_base # Avoid zero spacing
    print(f"Avg X tick diff (rounded): {avg_tick_diff}")

    total_tick_span = avg_tick_diff * (num_ticks - 1)
    min_inset = avg_tick_diff * 0.5 # Min distance from edge
    # Calculate starting tick, trying to center, respecting inset & rounding
    first_tick = max(round(x_tick_min / tick_rounding_base) * tick_rounding_base + min_inset,
                     round((x_tick_min + (x_tick_calc_range - total_tick_span) / 2) / tick_rounding_base) * tick_rounding_base)

    custom_xticks = [first_tick + i * avg_tick_diff for i in range(num_ticks)]

    # Adjust if ticks fall outside bounds
    for _ in range(max_adjustments):
        if custom_xticks[0] < x_tick_min + min_inset * 0.99: # Add tolerance
            custom_xticks = [tick + avg_tick_diff for tick in custom_xticks]
        elif custom_xticks[-1] > x_tick_max - min_inset * 0.99: # Add tolerance
            custom_xticks = [tick - avg_tick_diff for tick in custom_xticks]
        else: break

    # Final fallback: if still out of bounds, recalculate spacing
    if custom_xticks[0] < x_tick_min + min_inset * 0.99 or custom_xticks[-1] > x_tick_max - min_inset * 0.99 :
        print("X-Tick Fallback Adjustment Required")
        inset_adjusted_range = x_tick_max - (x_tick_min + min_inset)
        if inset_adjusted_range > 0:
            adjusted_tick_diff = inset_adjusted_range / (num_ticks - 1)
            avg_tick_diff = round(adjusted_tick_diff / tick_rounding_base) * tick_rounding_base
            if avg_tick_diff == 0: avg_tick_diff = tick_rounding_base
            first_tick = round((x_tick_min + min_inset) / tick_rounding_base) * tick_rounding_base
            custom_xticks = [first_tick + i * avg_tick_diff for i in range(num_ticks)]
            # Fine-tune position
            for _ in range(max_adjustments):
                 if custom_xticks[-1] > x_tick_max - min_inset * 0.99: first_tick -= tick_rounding_base
                 elif custom_xticks[0] < x_tick_min + min_inset * 0.99: first_tick += tick_rounding_base
                 else: break
                 custom_xticks = [first_tick + i * avg_tick_diff for i in range(num_ticks)]
        else: # Range too small for inset, just place ticks as calculated initially
             print("Warning: X-axis range too small for inset adjustment.")
             pass # Keep the possibly poorly fitting ticks

else: # Handle zero range or num_ticks <= 1
    print("Warning: Cannot calculate optimal X ticks due to range or num_ticks.")
    custom_xticks = np.linspace(x_limits[0], x_limits[1], num_ticks) # Default linear spacing

custom_xticks = np.array(custom_xticks)
print(f"Final X Ticks: {custom_xticks}")


# --- Y-axis Ticks (using the same logic as X-axis) ---
print("\n--- Y-Tick Calculation ---")
y_axis_range = y_limits[1] - y_limits[0]
y_tick_min = y_limits[0] + tick_margin_factor * y_axis_range
y_tick_max = y_limits[1] - tick_margin_factor * y_axis_range
y_tick_calc_range = y_tick_max - y_tick_min

if y_tick_calc_range > 0 and num_ticks > 1:
    # Generate initial yticks
    initial_yticks = np.linspace(y_tick_min, y_tick_max, num_ticks)
    y_tick_diffs = np.diff(initial_yticks)
    avg_y_tick_diff = round(np.mean(y_tick_diffs) / tick_rounding_base) * tick_rounding_base
    if avg_y_tick_diff == 0: avg_y_tick_diff = tick_rounding_base # Avoid zero spacing
    print(f"Avg Y tick diff (rounded): {avg_y_tick_diff}")

    total_y_tick_span = avg_y_tick_diff * (num_ticks - 1)
    min_y_inset = avg_y_tick_diff * 0.5 # Min distance from edge
    # Calculate starting tick, trying to center, respecting inset & rounding
    first_y_tick = max(round(y_tick_min / tick_rounding_base) * tick_rounding_base + min_y_inset,
                       round((y_tick_min + (y_tick_calc_range - total_y_tick_span) / 2) / tick_rounding_base) * tick_rounding_base)

    custom_yticks = [first_y_tick + i * avg_y_tick_diff for i in range(num_ticks)]

    # Adjust if ticks fall outside bounds
    for _ in range(max_adjustments):
        if custom_yticks[0] < y_tick_min + min_y_inset * 0.99: # Add tolerance
            custom_yticks = [tick + avg_y_tick_diff for tick in custom_yticks]
        elif custom_yticks[-1] > y_tick_max - min_y_inset * 0.99: # Add tolerance
            custom_yticks = [tick - avg_y_tick_diff for tick in custom_yticks]
        else: break

    # Final fallback: if still out of bounds, recalculate spacing
    if custom_yticks[0] < y_tick_min + min_y_inset * 0.99 or custom_yticks[-1] > y_tick_max - min_y_inset * 0.99:
        print("Y-Tick Fallback Adjustment Required")
        inset_y_adjusted_range = y_tick_max - (y_tick_min + min_y_inset)
        if inset_y_adjusted_range > 0 and (num_ticks -1) > 0 :
            adjusted_y_tick_diff = inset_y_adjusted_range / (num_ticks - 1)
            avg_y_tick_diff = round(adjusted_y_tick_diff / tick_rounding_base) * tick_rounding_base
            if avg_y_tick_diff == 0: avg_y_tick_diff = tick_rounding_base
            first_y_tick = round((y_tick_min + min_y_inset) / tick_rounding_base) * tick_rounding_base
            custom_yticks = [first_y_tick + i * avg_y_tick_diff for i in range(num_ticks)]
             # Fine-tune position
            for _ in range(max_adjustments):
                 if custom_yticks[-1] > y_tick_max - min_y_inset * 0.99: first_y_tick -= tick_rounding_base
                 elif custom_yticks[0] < y_tick_min + min_y_inset * 0.99: first_y_tick += tick_rounding_base
                 else: break
                 custom_yticks = [first_y_tick + i * avg_y_tick_diff for i in range(num_ticks)]
        else: # Range too small for inset, just place ticks as calculated initially
             print("Warning: Y-axis range too small for inset adjustment.")
             pass # Keep the possibly poorly fitting ticks

else: # Handle zero range or num_ticks <= 1
    print("Warning: Cannot calculate optimal Y ticks due to range or num_ticks.")
    custom_yticks = np.linspace(y_limits[0], y_limits[1], num_ticks) # Default linear spacing


custom_yticks = np.array(custom_yticks)
print(f"Final Y Ticks: {custom_yticks}")
print()

# --- Set Ticks and Labels ---
ax.set_xticks(custom_xticks)
ax.set_yticks(custom_yticks)
ax.set_xticklabels([f"{int(round(tick))}" for tick in custom_xticks], fontsize=15) # Use round for safety
ax.set_yticklabels([f"{int(round(tick))}" for tick in custom_yticks], rotation=90, va='center', fontsize=15) # va='center' often better for rotated

# --- Twin Axes for Top/Right Ticks ---
ax2, ax3 = ax.twiny(), ax.twinx()
ax2.set_xlim(ax.get_xlim())
ax3.set_ylim(ax.get_ylim())
ax2.set_xticks(custom_xticks)
ax3.set_yticks(custom_yticks)
ax2.set_xticklabels([f"{int(round(tick))}" for tick in custom_xticks], fontsize=15)
ax3.set_yticklabels([f"{int(round(tick))}" for tick in custom_yticks], rotation=270, va='center', fontsize=15) # va='center'

# --- Grid Lines ---
# Option 1: Use ax.grid and let twin axes handle their sides (cleaner)
ax.grid(True, which='major', axis='x', linestyle='--', linewidth=0.75, color='gray')
ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.75, color='gray')
# Ensure grid is drawn based on primary axis ticks even with twins
ax.xaxis.set_major_locator(plt.FixedLocator(custom_xticks))
ax.yaxis.set_major_locator(plt.FixedLocator(custom_yticks))
ax2.xaxis.set_major_locator(plt.FixedLocator(custom_xticks)) # Ensures ax2 grid aligns if needed
ax3.yaxis.set_major_locator(plt.FixedLocator(custom_yticks)) # Ensures ax3 grid aligns if needed


# Option 2: Explicit lines (commented out - Option 1 is usually sufficient)
# ax.grid(False) # Turn off default grid if drawing manually
# for tick in custom_xticks: ax.axvline(x=tick, color='gray', linestyle='--', linewidth=0.75)
# for tick in custom_yticks: ax.axhline(y=tick, color='gray', linestyle='--', linewidth=0.75)

# Remove default tick marks on twin axes if desired (cleaner look)
ax2.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False, labeltop=True)
ax3.tick_params(axis='y', which='both', left=False, right=False, labelleft=False, labelright=True)


# --- Final Scale Calculation ---
print("--- Scale Calculation ---")
dynamic_scale = calculate_scale(ax, fig_width_inches=25, fig_height_inches=22)
print(f"Scale 1:{dynamic_scale}")

# --- Display Plot ---
plt.show()
