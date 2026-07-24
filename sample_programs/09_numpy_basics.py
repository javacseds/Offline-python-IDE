# Lab Program 09: NumPy Array Computations
try:
    import numpy as np
    print("NumPy Version:", np.__version__)

    # Create 1D and 2D arrays
    arr1 = np.array([10, 20, 30, 40, 50])
    arr2 = np.array([[1, 2, 3], [4, 5, 6]])

    print("1D Array:", arr1)
    print("Array Mean:", np.mean(arr1))
    print("Array Sum:", np.sum(arr1))
    print("
2D Matrix Shape:", arr2.shape)
    print("2D Matrix Transpose:\n", arr2.T)
except ImportError:
    print("NumPy is not installed. Please use the Package Manager tab to install NumPy.")
