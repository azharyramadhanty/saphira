from typing import Annotated, get_type_hints, get_origin, get_args
from functools import wraps


def check_value_range(func):  # make custom annotated, how this works bts in fastapi
    @wraps(func)
    def wrapped(x):
        type_hints = get_type_hints(func, include_extras=True)
        hint = type_hints['x']
        if get_origin(hint) is Annotated:
            # *hint_args is to get the rest of the metadata for future proof
            hint_type, *hint_args = get_args(hint)
            low, high = hint_args[0]
            if not low <= x <= high:
                raise ValueError(f"(x) falls outside boundary {low}-{high}")
        # execute function once all checks passed
        return func(x)
    return wrapped


@check_value_range
def double(x: Annotated[int, (0, 10)]) -> int:
    return x * 2
