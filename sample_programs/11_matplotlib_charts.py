# Lab Program 11: Matplotlib Data Visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np

    # Generate sample data
    x = np.linspace(0, 10, 100)
    y_sine = np.sin(x)
    y_cosine = np.cos(x)

    plt.figure(figsize=(7, 4))
    plt.plot(x, y_sine, label="Sine Wave", color="#1e3a8a", linewidth=2)
    plt.plot(x, y_cosine, label="Cosine Wave", color="#f97316", linewidth=2, linestyle="--")

    plt.title("GITAMW CSE - Mathematical Function Plot", fontsize=12, fontweight="bold")
    plt.xlabel("X Value", fontsize=10)
    plt.ylabel("Y Value", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()

    # In GITAMW Python Smart IDE, plots rendered via plt.show()
    # are automatically displayed directly in the IDE Output Window!
    plt.show()
    print("Chart plotted and rendered successfully!")
except ImportError:
    print("Matplotlib is not installed. Install Matplotlib via the Package Manager tab.")
