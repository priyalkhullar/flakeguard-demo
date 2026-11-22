import random

import pytest


@pytest.fixture(autouse=True)
def _fixed_seed_without_pytest_randomly(request):
    """Keep `random` deterministic when pytest-randomly is not active.

    With pytest-randomly active, its --randomly-seed decides the draw in
    tests/test_sync.py, so any failure can be reproduced by passing the same seed.
    Without it (for example `-p no:randomly`), the seed is fixed at 0 and the draw is a pass.
    """
    if not request.config.pluginmanager.hasplugin("randomly"):
        random.seed(0)
    yield


import pytest
import inventory.cache as _flakeguard_cache


@pytest.fixture(autouse=True)
def _flakeguard_restore_cache():
    before = dict(_flakeguard_cache.CACHE)
    yield
    _flakeguard_cache.CACHE.clear()
    _flakeguard_cache.CACHE.update(before)
