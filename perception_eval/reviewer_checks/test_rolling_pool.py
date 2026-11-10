"""Exercise bounded scheduling with real threads and synchronization events."""
from threading import Event, Lock

from rolling_pool import rolling_map


class TestRollingPool:
    """Completion of a short task must allow new work before a long task ends."""

    def test_refills_before_slow_task_finishes(self) -> None:
        """The third job releases the first, proving no whole-batch barrier."""
        third_started = Event()
        guard = Lock()
        active = 0
        peak = 0

        def worker(number: int) -> int:
            """Run real synchronized work and return its index (int)."""
            nonlocal active, peak
            with guard:
                active += 1
                peak = max(peak, active)
            if number == 0:
                assert third_started.wait(5)
            elif number == 2:
                third_started.set()
            with guard:
                active -= 1
            return number

        results = rolling_map(range(6), worker, 2, lambda _: False)
        assert sorted(results) == list(range(6))
        assert peak <= 2 and active == 0

    def test_stop_drains_running_job_without_submitting_more(self) -> None:
        """A terminal result stops new submissions and preserves in-flight work."""
        second_started = Event()
        release_second = Event()
        executed: list[int] = []

        def worker(number: int) -> int:
            """Keep the second task active until the first stop is observed."""
            executed.append(number)
            if number == 0:
                assert second_started.wait(5)
            elif number == 1:
                second_started.set()
                assert release_second.wait(5)
            return number

        def observed(number: int) -> None:
            """Release the remaining task when result zero is delivered."""
            if number == 0:
                release_second.set()

        results = rolling_map(range(5), worker, 2, lambda n: n == 0, observed)
        assert sorted(results) == [0, 1]
        assert sorted(executed) == [0, 1]

    def test_matches_sequential_reference_without_stop(self) -> None:
        """The bounded pool preserves every result exactly once."""
        expected = [number * number for number in range(17)]
        actual = rolling_map(range(17), lambda number: number * number, 4, lambda _: False)
        assert sorted(actual) == sorted(expected)
