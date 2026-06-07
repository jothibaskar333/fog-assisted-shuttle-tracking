import matplotlib.pyplot as plt

# Simulated values (based on experiments)
cloud_only_latency = [900, 920, 910, 905, 915]  # ms
fog_based_latency = [250, 260, 245, 255, 248]  # ms

cloud_only_packets = 20
edge_filtered_packets = 8

# Plot latency comparison
plt.figure()
plt.plot(cloud_only_latency, label="Cloud Only Latency")
plt.plot(fog_based_latency, label="Fog-Based Latency")
plt.xlabel("Request Count")
plt.ylabel("Latency (ms)")
plt.title("Latency Comparison: Cloud vs Fog")
plt.legend()
plt.show()

# Plot bandwidth comparison
plt.figure()
labels = ["Cloud Only", "Edge Filtered"]
packets = [cloud_only_packets, edge_filtered_packets]
plt.bar(labels, packets)
plt.xlabel("Architecture")
plt.ylabel("Number of Packets Sent")
plt.title("Bandwidth Usage Comparison")
plt.show()
