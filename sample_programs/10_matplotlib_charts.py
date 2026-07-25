# Lab Program 10: Matplotlib Data Visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.linspace(0, 10, 100)
    plt.figure(figsize=(7, 4))
    plt.plot(x, np.sin(x), label="Sine", color="#1e3a8a", linewidth=2)
    plt.plot(x, np.cos(x), label="Cosine", color="#f97316", linewidth=2, linestyle="--")
    plt.title("GITAMW CSE - Mathematical Function Plot")
    plt.legend()
    plt.show()
    print("Chart rendered successfully!")
except ImportError:
    print("Matplotlib not installed. Install via Package Manager.")
