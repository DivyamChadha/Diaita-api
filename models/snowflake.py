from __future__ import annotations

from datetime import datetime, timedelta, timezone

# DIAITA_EPOCH = 1640995200 # Saturday, 1 January 2022 12:00:00 AM
DIAITA_EPOCH = 1609459200 # Friday, 1 January 2021 12:00:00 AM (TEMPORARY)

class Snowflake:
    __slots__ = ( 'timestamp', 'worker_id', 'sequence', )

    def __init__(self, timestamp: datetime, worker_id: int, sequence: int) -> None:
        delta = timestamp - datetime.fromtimestamp(DIAITA_EPOCH, timezone.utc)
        self.timestamp = int(delta / timedelta(milliseconds=1))
        self.worker_id = worker_id
        self.sequence = sequence

    @classmethod
    def now(cls, worker_id: int, sequence: int):
        return cls(datetime.now(timezone.utc), worker_id, sequence)

    def __str__(self) -> str:
        return f'{int(self):064b}'

    def __int__(self) -> int:
        return (self.timestamp << 22) + (self.worker_id << 12) + self.sequence

    def __repr__(self) -> str:
        return bin(int(self))
    
    def __lt__(self, other: Snowflake) -> bool:
        return int(self) < int(other)

    def __le__(self, other: Snowflake) -> bool:
        return int(self) <= int(other)

    def __gt__(self, other: Snowflake) -> bool:
        return int(self) > int(other)

    def __ge__(self, other: Snowflake) -> bool:
        return int(self) >= int(other)

    def __eq__(self, other: Snowflake) -> bool:
        return int(self) == int(other)

    def __ne__(self, other: Snowflake) -> bool:
        return int(self) != int(other)

    @property
    def created_on(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp + DIAITA_EPOCH, timezone.utc)
