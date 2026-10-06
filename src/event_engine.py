class EventEngine:
    """
    Phase 4 event engine.

    Watches each tracked object in restricted zones and creates events:
      ENTER               - object confirmed inside a restricted zone
      LOITERING           - object stayed longer than dwell_seconds
                            (fires once per stay)
      EXIT                - object left the zone (includes total stay duration)
      REPEATED_VIOLATION  - the same track entered a restricted zone
                            repeat_limit times within repeat_window seconds
                            (fires once, then the count starts again)

    Every event fires only once, never on every frame.
    """

    def __init__(self, restricted_zones, dwell_seconds,
                 repeat_limit, repeat_window_seconds):
        self.restricted_zones = set(restricted_zones)
        self.dwell_seconds = dwell_seconds
        self.repeat_limit = repeat_limit
        self.repeat_window_seconds = repeat_window_seconds

        # track_id -> record of the current stay in a restricted zone
        self.stays = {}
        # track_id -> list of recent entry times (seconds)
        self.entry_times = {}

    def _make_event(self, event_type, record, track_id, duration, count=0):
        return {
            "event_type": event_type,
            "object_type": record["type"],
            "track_id": track_id,
            "zone_name": record["zone"],
            "duration": duration,
            "confidence": record["conf"],
            "count": count,
        }

    def _check_repeated(self, record, track_id, now):
        """Record an entry and return a REPEATED_VIOLATION event if the
        track has entered repeat_limit times inside the time window."""
        times = self.entry_times.setdefault(track_id, [])
        times.append(now)

        # Keep only entries inside the time window
        cutoff = now - self.repeat_window_seconds
        times[:] = [t for t in times if t >= cutoff]

        if len(times) >= self.repeat_limit:
            count = len(times)
            span = times[-1] - times[0]
            times.clear()  # start counting again after the alert
            return self._make_event(
                "REPEATED_VIOLATION", record, track_id, span, count
            )
        return None

    def update(self, track_id, object_type, zone, confidence, now):
        """
        Call once per frame for every tracked object, with its CONFIRMED zone.
        `now` is the current time in seconds.
        Returns a list of new events (usually empty).
        """
        events = []
        record = self.stays.get(track_id)

        if record is not None:
            record["conf"] = confidence
            record["type"] = object_type

        # Left the zone it was in (or moved to a different zone)
        if record is not None and record["zone"] != zone:
            duration = now - record["entered_at"]
            events.append(self._make_event("EXIT", record, track_id, duration))
            del self.stays[track_id]
            record = None

        # Entered a restricted zone
        if record is None and zone in self.restricted_zones:
            record = {
                "type": object_type,
                "zone": zone,
                "entered_at": now,
                "loiter_fired": False,
                "conf": confidence,
            }
            self.stays[track_id] = record
            events.append(self._make_event("ENTER", record, track_id, 0.0))

            repeated = self._check_repeated(record, track_id, now)
            if repeated is not None:
                events.append(repeated)

        # Dwell time check (loitering)
        if record is not None:
            duration = now - record["entered_at"]
            if (not record["loiter_fired"]) and duration >= self.dwell_seconds:
                record["loiter_fired"] = True
                events.append(
                    self._make_event("LOITERING", record, track_id, duration)
                )

        return events

    def get_dwell(self, track_id, now):
        """Seconds the object has stayed in its restricted zone (0 if none)."""
        record = self.stays.get(track_id)
        if record is None:
            return 0.0
        return now - record["entered_at"]

    def remove_track(self, track_id, now):
        """Call when a track is lost. Closes its stay with an EXIT event."""
        record = self.stays.pop(track_id, None)
        if record is None:
            return []
        duration = now - record["entered_at"]
        return [self._make_event("EXIT", record, track_id, duration)]