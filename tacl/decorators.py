from functools import wraps

from . import constants
from .exceptions import MalformedResultsError


def requires_columns(required_cols):
    """Decorator that raises a `MalformedResultsError` if any of
    `required_cols` is not present as a column in the matches of the
    `Results` object bearing the decorated method.

    :param required_cols: names of required columns
    :type required_cols: `list` of `str`

    """
    def dec(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            actual_cols = list(args[0]._matches.columns)
            missing_cols = []
            for required_col in required_cols:
                if required_col not in actual_cols:
                    missing_cols.append('"{}"'.format(required_col))
            if missing_cols:
                raise MalformedResultsError(
                    constants.MISSING_REQUIRED_COLUMNS_ERROR.format(
                        ', '.join(missing_cols)))
            return f(*args, **kwargs)
        return decorated_function
    return dec
