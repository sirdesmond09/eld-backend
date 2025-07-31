from functools import wraps
from typing import Any, Callable


def inject_payload_with_data(func) -> Callable[..., Any]:
    """Alter request payload cleanly and inject data into the payload."""

    @wraps(func)
    def wrapper(view, *args: tuple, **kwargs: dict) -> Any:
        data = view.request.data.copy()
        data.update(**kwargs)
        view.request._full_data = data
        return func(view, *args, **kwargs)

    return wrapper 