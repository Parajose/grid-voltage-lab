# Grid Voltage Lab

**Explore feeder voltage. Understand the trade-offs.**

Compare a balanced radial feeder before and after ideal reactive support. Change load, impedance and support location, then inspect voltage and losses.

Built by [Joseph Tetteh (TJay)](https://github.com/Parajose) · Python + vanilla HTML/CSS/JavaScript · MIT license

## Run in under a minute

Requires **Python 3.10+**. There are **no third-party dependencies**.

```bash
git clone https://github.com/Parajose/grid-voltage-lab.git
cd grid-voltage-lab
python app.py
```

On Windows, use `py app.py` if `python` is unavailable. Open **http://127.0.0.1:8000**. Run one project at a time because all use port 8000. Stop with Ctrl+C. Open through the server, not by double-clicking `index.html`.

The sample runs automatically. Edit the JSON and click **Analyse scenario**, or use **Reset sample**. Each result table has a CSV export. Invalid input clears old results and explains the error.

## Features

- Responsive dashboard with sample data and interactive scenario inputs
- Transparent calculations in a separate, testable Python module
- CSV exports and readable input validation
- Local HTTP API with no required account or external service
- Automated numerical and edge-case checks using standard-library unittest

## Method and units

The source is fixed at 1∠0 pu. Each non-source bus has one upstream branch, series R + jX and a constant-PQ load. All inputs use **per unit on one consistent balanced three-phase base**. For physical inputs, use Zbase = VLL,base² / S3φ,base and divide three-phase P and Q by S3φ,base.

Each iteration computes Iload = conjugate(S / V), sums downstream currents in a backward sweep, and updates Vchild = Vparent − Zbranch × Ibranch in a forward sweep. Stop when the maximum complex voltage change is below 1e−10 pu, with a 500-iteration cap. Branch active losses are |I|²R. Positive support subtracts Q from the selected bus load.

The dashboard compares the same load level with zero support and with the requested support. CSV contains scenario bus voltage, phase angle, upstream branch current and active loss. `baseline` and `scenario` in the JSON API include source power and total losses.

### What the tool does not establish

This is an educational steady-state **radial distribution** model, not a GRIDCo transmission-network model. Voltage magnitude ranking does not calculate voltage-collapse margin or an accepted voltage-stability index. Fixed-Q injection is not a dynamic FACTS device model or an optimal placement algorithm. No unbalance, regulators, shunts, thermal limits, transformer tap control or operational recommendations are included. The 0.95 pu threshold is illustrative.

### Useful next steps

Add validated benchmark feeders, line thermal ratings and continuation load flow before using the project for research comparisons. Validate against an independent solver on the same bases and assumptions.

## Project layout

| File | Purpose |
| --- | --- |
| `app.py` | Local HTTP server and JSON API |
| `core.py` | Validation and domain calculations |
| `index.html` | Responsive interface and safe DOM rendering |
| `sample.json` | Reproducible fictional sample |
| `test_core.py` | Calculation and validation tests |
| `LICENSE` | MIT license |

## Test

```bash
python -m unittest -v
```

## API

`GET /api/demo` returns sample inputs. `POST /api/analyse` accepts the same JSON shape and returns `summary`, `rows`, `chart`, `notes` and project-specific details. Invalid input returns HTTP 400 with an `error` message. Requests are limited to 1 MB. The server is intentionally local-only.

```bash
curl -H "Content-Type: application/json" --data-binary @sample.json http://127.0.0.1:8000/api/analyse
```

## Development status

Working initial portfolio release. Tests cover the core calculations and selected failure cases; this is not an independently certified engineering or institutional system. Contributions that add benchmark validation, accessibility improvements and documented use cases are welcome.
