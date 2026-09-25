"""Thread-safe, process-memory-only aggregation for anonymous plays."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from threading import Lock

from core import PlayRecord, STAY, SWITCH


@dataclass(frozen=True)
class AggregateSummary:
    play_count: int
    stay_count: int
    switch_count: int
    stay_rate: float | None
    switch_rate: float | None
    benchmark_agreement_rate: float | None
    mean_switching_difficulty: float | None
    mean_personalization_concern: float | None
    mean_privacy_concern: float | None
    mean_trust: float | None


@dataclass(frozen=True)
class PeerSnapshot:
    portability_condition: str
    same_condition: AggregateSummary
    overall: AggregateSummary


def _summarize(records: tuple[PlayRecord, ...]) -> AggregateSummary:
    count = len(records)
    if count == 0:
        return AggregateSummary(
            play_count=0,
            stay_count=0,
            switch_count=0,
            stay_rate=None,
            switch_rate=None,
            benchmark_agreement_rate=None,
            mean_switching_difficulty=None,
            mean_personalization_concern=None,
            mean_privacy_concern=None,
            mean_trust=None,
        )

    stay_count = sum(record.final_choice == STAY for record in records)
    switch_count = sum(record.final_choice == SWITCH for record in records)
    return AggregateSummary(
        play_count=count,
        stay_count=stay_count,
        switch_count=switch_count,
        stay_rate=stay_count / count,
        switch_rate=switch_count / count,
        benchmark_agreement_rate=(
            sum(record.final_benchmark_agreement for record in records) / count
        ),
        mean_switching_difficulty=fmean(
            record.perceived_switching_difficulty for record in records
        ),
        mean_personalization_concern=fmean(
            record.personalization_concern for record in records
        ),
        mean_privacy_concern=fmean(record.privacy_concern for record in records),
        mean_trust=fmean(record.trust for record in records),
    )


class InMemoryPlayStore:
    """Aggregate structured plays without a persistent backend."""

    persistence_enabled = False

    def __init__(self) -> None:
        self._lock = Lock()
        self._records: list[PlayRecord] = []
        self._submitted_play_ids: set[str] = set()

    def add_play(self, record: PlayRecord) -> bool:
        """Add once; return False for a duplicate play ID."""

        with self._lock:
            if record.play_id in self._submitted_play_ids:
                return False
            self._records.append(record)
            self._submitted_play_ids.add(record.play_id)
            return True

    def snapshot_and_add(self, record: PlayRecord) -> tuple[PeerSnapshot, bool]:
        """Atomically summarize prior plays, then add the current play once."""

        with self._lock:
            records = tuple(self._records)
            same_condition = tuple(
                prior
                for prior in records
                if prior.portability_condition == record.portability_condition
            )
            snapshot = PeerSnapshot(
                portability_condition=record.portability_condition,
                same_condition=_summarize(same_condition),
                overall=_summarize(records),
            )
            if record.play_id in self._submitted_play_ids:
                return snapshot, False
            self._records.append(record)
            self._submitted_play_ids.add(record.play_id)
            return snapshot, True

    def prior_snapshot(self, portability_condition: str) -> PeerSnapshot:
        """Summarize all records already present at the instant of the call."""

        with self._lock:
            records = tuple(self._records)
        same_condition = tuple(
            record
            for record in records
            if record.portability_condition == portability_condition
        )
        return PeerSnapshot(
            portability_condition=portability_condition,
            same_condition=_summarize(same_condition),
            overall=_summarize(records),
        )

    def size(self) -> int:
        with self._lock:
            return len(self._records)

    def records_for_testing(self) -> tuple[PlayRecord, ...]:
        with self._lock:
            return tuple(self._records)

    def clear_for_testing(self) -> None:
        with self._lock:
            self._records.clear()
            self._submitted_play_ids.clear()
