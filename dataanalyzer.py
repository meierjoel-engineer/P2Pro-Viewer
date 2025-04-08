import numpy as np

import matplotlib.pyplot as plt

# Load the data
frame_data = np.load('frame_data_100.npy')

# Print basic info about the data
print(f"Data shape: {frame_data.shape}")
print(f"Data type: {frame_data.dtype}")

# If it's a multi-dimensional array, flatten it for sorting
if len(frame_data.shape) > 1:
    flattened_data = frame_data.flatten()
else:
    flattened_data = frame_data

# Sort the data
sorted_data = np.sort(flattened_data)

# Count and print number of unique values
unique_values = np.unique(flattened_data)
print(f"Number of unique values: {len(unique_values)}")
print(f"Min value: {np.min(flattened_data)}")
print(f"Max value: {np.max(flattened_data)}")
print(f"Range: {np.max(flattened_data) - np.min(flattened_data)}")

# Optional: print first few unique values to see the step size
print(f"First 10 unique values: {unique_values[:10]}")
print(f"Last 10 unique values: {unique_values[-10:]}")

# Calculate average step size between consecutive unique values
if len(unique_values) > 1:
    avg_step = np.mean(np.diff(unique_values))
    print(f"Average step size between consecutive unique values: {avg_step:.2f}")

# Plot the sorted data to see discrete steps
plt.figure(figsize=(12, 6))
plt.plot(sorted_data, '-o', markersize=2)
plt.title('Sorted Frame Data Values')
plt.xlabel('Index')
plt.ylabel('Pixel Value')
plt.grid(True)

# Create a histogram to see the distribution of values
plt.figure(figsize=(12, 6))
plt.hist(flattened_data, bins=50, alpha=0.7)
plt.title('Histogram of Frame Data Values')
plt.xlabel('Pixel Value')
plt.ylabel('Frequency')
plt.grid(True)

# Show both plots
plt.tight_layout()
plt.show()