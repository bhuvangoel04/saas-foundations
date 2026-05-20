from datetime import datetime
from django.utils import timezone

def timestamp_as_datetime(ts):
    if ts is None:
        return None
    try:
        dt = datetime.fromtimestamp(int(ts))
        return timezone.make_aware(dt)
    except Exception:
        return None
