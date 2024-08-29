"""
Searching a pandas DataFrame.
"""
import pandas as pd

def query_df(df: pd.DataFrame, search_kwargs: dict[str, any]) -> pd.DataFrame | None:
    """
    Search a DataFrame for row(s) that match the provided column: values in search_kwargs.

    Required arguments:
    * df: DataFrame, DataFrame to search
    * search_kwargs: dict[str, any], column: value pairs to query.

    @return DataFrame if results are found, else return None.
    """
    # Generate query
    query_str_segments = []
    for col, val in search_kwargs.items():
        if isinstance(val, str):
            val = f'"{val}"'
        query_str_segments.append(f'`{col}`=={val}')
    query_str = ' & '.join(query_str_segments)
    
    # Make query
    result = None
    try:
        result = df.query(query_str)
    except:
        return None
    
    return None if result.empty else result