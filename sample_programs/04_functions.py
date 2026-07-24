# Lab Program 04: Python Functions & Recursion

def calculate_factorial(n: int) -> int:
    """Calculates factorial of n using recursion."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def is_prime(number: int) -> bool:
    """Checks if a number is prime."""
    if number <= 1:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True

print("Factorial of 5:", calculate_factorial(5))
print("Is 17 Prime?:", is_prime(17))
print("Is 24 Prime?:", is_prime(24))
