"""Keep a bounded pool occupied while safely draining after a stop result."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from typing import TypeVar

Job = TypeVar('Job')
Result = TypeVar('Result')


def rolling_map(jobs: Iterable[Job], worker: Callable[[Job], Result], workers: int,
                should_stop: Callable[[Result], bool],
                on_result: Callable[[Result], None] | None = None) -> list[Result]:
    """Refill each free slot, stopping new submissions after a terminal result.

    Args:
        jobs (Iterable[Job]): Finite jobs in their predeclared submission order.
        worker (Callable[[Job], Result]): Execute and durably save one job.
        workers (int): Positive maximum simultaneous jobs.
        should_stop (Callable[[Result], bool]): True stops all future submissions.
        on_result (Callable[[Result], None] | None): Optional progress callback.

    Returns:
        list[Result]: Every submitted job's result, including jobs drained after
        a stop. A stop never cancels an already-running request. Worker exceptions
        propagate after the executor waits for all already-submitted jobs.
    """
    if workers < 1:
        raise ValueError('workers must be positive')
    remaining = iter(jobs)
    results: list[Result] = []
    stopped = False
    exhausted = False
    with ThreadPoolExecutor(max_workers=workers) as pool:
        active: set[Future[Result]] = set()
        while active or not (stopped or exhausted):
            while len(active) < workers and not (stopped or exhausted):
                try:
                    job = next(remaining)
                except StopIteration:
                    exhausted = True
                    break
                active.add(pool.submit(worker, job))
            if not active:
                break
            done, active = wait(active, return_when=FIRST_COMPLETED)
            for future in done:
                result = future.result()
                results.append(result)
                stopped = should_stop(result) or stopped
                if on_result is not None:
                    on_result(result)
    return results
