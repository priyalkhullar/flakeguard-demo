# flakeguard-demo

A small Python "inventory" project with pytest tests. **It is deliberately seeded with test
faults for the FlakeGuard demo.** The faults are not on `main`: `main` is clean, and the faults
arrive through pull requests so that FlakeGuard can review them.

```bash
pip install -e ".[test]"      # installs pytest and pytest-randomly
```

## How the demo is laid out

| Branch / PR | What it does | What FlakeGuard should say |
|---|---|---|
| `main` | Clean. Three tests, all pass in every order. | Nothing to find |
| **Act 1** pull request | Adds one deterministic test (`tests/test_inventory_total.py`) that uses only local objects. | No evidence of flakiness in 10 shuffled runs |
| **Act 2** pull request | A `git revert` of the "Make main clean" commit. It brings back the four seeded faults below. | The findings in the next section |

## The seeded faults (restored by the Act 2 pull request)

| Test | Fault | What FlakeGuard should say |
|---|---|---|
| `tests/test_warmup.py::test_cache_warm` | **Polluter.** Writes `CACHE["sku-1"] = 40` (module-level dict, `src/inventory/cache.py:3`) and never clears it. | Polluter |
| `tests/test_report.py::test_report_total` | **Order-dependent victim.** Reads `CACHE` through `Report.total` and fails if `test_cache_warm` ran first. | Flaky, order-dependent |
| `tests/test_stock.py::test_reserve_negative` | **Real bug.** `StockService.reserve` accepts a negative quantity, so this test fails in every run, in any order. | Real failure (cannot be quarantined) |
| `tests/test_sync.py::test_sync_timeout` | **Rare seeded failure.** The simulated remote end times out when a draw from Python's shared `random` generator is below 0.1. The draw is decided by the `pytest-randomly` seed, so a failure can be reproduced. About 9% of seeds fail. | Unknown (too few failures to call it flaky) |

With the faults restored, every test passes in default order (`pytest -p no:randomly`) **except
`test_reserve_negative`, which fails by design in every run.** The order-dependent test passes in
default order because `test_warmup.py` sorts after `test_report.py`, so the polluter runs last.

## Scans use fixed seeds 1 to 10

Each shuffled run uses a pytest-randomly seed. With random seeds, 10 shuffled runs hit a failing
seed only about 61% of the time (11 of 120 seeds fail), so about 4 scans in 10 would show no sync
failure at all. The workflow in `.github/workflows/flakeguard.yml` therefore passes
`seed_start: 1`, which gives the seeds 1 to 10. Seed 4 is the only failing seed in that range,
which gives a reproducible "1 failure in 10 runs". The seeds are shown on the Live screen and in
the comment FlakeGuard posts ("shuffled seeds 1 to 10").

`test_sync_timeout` by seed, measured with
`pytest -p randomly --randomly-seed=N tests/test_sync.py::test_sync_timeout`:

| Seed | 1 | 2 | 3 | **4** | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Result | pass | pass | pass | **fail** | pass | pass | pass | pass | pass | pass |

## Reproduce a fault by hand (on the Act 2 branch)

```bash
pytest -p no:randomly tests/test_warmup.py::test_cache_warm tests/test_report.py::test_report_total   # fails
pytest -p no:randomly tests/test_report.py::test_report_total                                          # passes
pytest -p randomly --randomly-seed=4 tests/test_sync.py::test_sync_timeout                             # fails
```

## Which FlakeGuard runs

`.github/workflows/flakeguard.yml` calls the reusable workflow in `vidipt9090/FlakeGuard`. The
`uses:` line names the FlakeGuard version. While FlakeGuard is being developed it is a branch;
for the demo it is pinned to a commit SHA, so that a later push to FlakeGuard cannot change what
the demo does.
