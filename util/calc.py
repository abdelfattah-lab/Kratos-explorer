import math

def get_portrait_square(n: int) -> tuple[int, int]:
    """
    Returns an approximate (rows, columns) that is as "squarish" as possible that is guaranteed to fit n (i.e., width * height >= n).
    """
    # find "squarish" layout
    side1 = math.floor(math.sqrt(n))
    side2 = math.ceil(n / float(side1))

    # favor portrait layout
    return max(side1, side2), min(side1, side2)