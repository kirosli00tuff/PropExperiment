"""pytest plugin (review only): caps fork-context Pool sizes at 4 processes (the review's compute limit).

test_e29_basket.py's fixture opens Pool(len(FIRMS)) = 5; with this plugin it gets 4 workers for the same 5 tasks.
No test logic changes.
"""
import multiprocessing.context as _ctx

_ORIG = _ctx.BaseContext.Pool


def _capped(self, processes=None, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
    return _ORIG(self, min(processes or 4, 4), *args, **kwargs)


_ctx.ForkContext.Pool = _capped
