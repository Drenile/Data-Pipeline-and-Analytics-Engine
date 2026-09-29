import json
import math
from datetime import datetime

import numpy as np
import pandas as pd


def to_json(report: dict) -> str:
    """Serialise a report as strict JSON. Escaping also neutralises control characters
    (e.g. terminal escape sequences) that could be hidden in CSV headers or values."""
    return json.dumps(_jsonable(report), indent=2, allow_nan=False)


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if value is pd.NaT:
        return None
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return value
