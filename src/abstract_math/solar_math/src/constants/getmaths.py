import math
import pandas as pd
import matplotlib.pyplot as plt

R_mi = 3958.7613  # mean Earth radius in miles

def exact_drop_miles(s_mi: float) -> float:
    return R_mi * (1 - math.cos(s_mi / R_mi))

def approx_drop_miles(s_mi: float) -> float:
    inches = 8 * s_mi**2
    return inches / 12 / 5280

distances = [1, 10, 100, 1000, 3000, 6215]
rows = []
for d in distances:
    exact = exact_drop_miles(d)
    approx = approx_drop_miles(d)
    err = approx - exact
    pct = (err / exact * 100) if exact else 0
    rows.append({
        "Distance (mi)": d,
        "Exact drop (mi)": exact,
        "8 in/mi² approx (mi)": approx,
        "Error (mi)": err,
        "Error (%)": pct,
    })

df = pd.DataFrame(rows)

# Save csv for convenience
csv_path = "drop_comparison_table.csv"
df.to_csv(csv_path, index=False)

# Plot
x = df["Distance (mi)"]
y1 = df["Exact drop (mi)"]
y2 = df["8 in/mi² approx (mi)"]

plt.figure(figsize=(8,5))
plt.plot(x, y1, marker="o", label="Exact drop")
plt.plot(x, y2, marker="o", label="8 in/mi² approximation")
plt.xlabel("Distance along surface (miles)")
plt.ylabel("Drop below starting tangent (miles)")
plt.title("Exact drop vs 8 in/mi² approximation")
plt.xscale("log")
plt.grid(True, alpha=0.3)
plt.legend()
img_path = "drop_comparison_chart.png"
plt.tight_layout()
plt.savefig(img_path, dpi=200)
plt.close()

print(img_path)
print(csv_path)
print(df.to_string(index=False, formatters={
    "Exact drop (mi)": "{:.6f}".format,
    "8 in/mi² approx (mi)": "{:.6f}".format,
    "Error (mi)": "{:.6f}".format,
    "Error (%)": "{:.3f}".format,
}))
