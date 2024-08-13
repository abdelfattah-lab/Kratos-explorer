import math
from pandas import DataFrame
from typing import Literal

def get_portrait_square(n: int) -> tuple[int, int]:
    """
    Returns an approximate (rows, columns) that is as "squarish" as possible that is guaranteed to fit n (i.e., width * height >= n).
    """
    # find "squarish" layout
    side1 = math.floor(math.sqrt(n))
    side2 = math.ceil(n / float(side1))

    # favor portrait layout
    return max(side1, side2), min(side1, side2)

def normalize_df(df: DataFrame, norm_type: Literal['min-max', 'mean'] = 'mean', cols: list[any] = None, min_max_vals: tuple[float, float] = None) -> None:
    """
    Normalizes specified columns of the DataFrame in-place.

    Optional arguments:
    * norm_type:'min-max'/'mean', type of normalization to apply.
    * cols:list[any], list of columns to apply normalization to. If None, then entire DataFrame is normalized. Default: None
    * min_max_vals:(min:float, max:float), minimum and maximum values to clamp to (i.e., normalization will be min-max). If None, then depends on norm_type. Default: None
    """
    extracted = df if cols is None else df[cols]
    
    if min_max_vals is not None:
        min_val, max_val = min_max_vals
        if min_val > max_val:
            raise ValueError(f"Minimum value {min_val} provided is larger than maximum value {max_val}!")
        
        diff = max_val - min_val
        extracted = min_val + diff * (extracted-extracted.min())/(extracted.max()-extracted.min())
    elif norm_type == 'min-max':
        extracted = (extracted-extracted.min())/(extracted.max()-extracted.min())
    elif norm_type == 'mean':
        extracted = (extracted-extracted.mean())/(extracted.std())
    else:
        raise ValueError("norm_type must be 'min-max' or 'mean'!")
    
    df.update(extracted)