from datetime import date
from typing import Optional, Tuple, Union

NumericOrDate = Union[float, int, date]


def validate_range(
    min_value: Optional[NumericOrDate],
    max_value: Optional[NumericOrDate],
    min_max_float_value: Optional[NumericOrDate] = 0,
) -> Tuple[Optional[NumericOrDate], Optional[NumericOrDate]]:
    if max_value is not None:
        if (isinstance(max_value, float) or isinstance(max_value, int)) and max_value < min_max_float_value:
            max_value = None

    if min_value is not None and max_value is not None:
        min_value, max_value = min(min_value, max_value), max(min_value, max_value)

    return min_value, max_value
