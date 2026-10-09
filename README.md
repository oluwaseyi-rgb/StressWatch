# StressWatch

**A Locust-based load testing script for simulating realistic concurrent user traffic against internal services.**

StressWatch defines simulated user behavior — browsing the homepage, viewing products, searching, submitting a form — with realistic wait times and weighted task frequency, then uses [Locust](https://locust.io/) to ramp up concurrent virtual users and measure how a service holds up under load. Built-in event hooks flag slow requests and failures as the test runs.

---

## What It Simulates

| Task | Weight | Behavior |
|---|---|---|
| View homepage | 5 | `GET /` — most frequent action |
| View product | 3 | `GET /api/products/{id}` with a random product ID |
| Search | 2 | `GET /api/search` with a random search term |
| Submit contact form | 1 | `POST /api/contact` with custom success/failure validation |

Weights control relative frequency — homepage views happen roughly 5x as often as form submissions, mimicking realistic traffic patterns rather than hammering every endpoint equally. Each simulated user also waits 1–3 seconds between actions (`wait_time`), rather than firing requests back to back.

---

## Requirements

- Python 3.7+
- `locust`

```bash
pip install locust --break-system-packages
```

---

## Usage

### Web UI mode (recommended)

Gives you live control over ramp-up and user count while the test runs:

```bash
locust -f stresswatch.py --host https://your-internal-service.company.com
```

Then open `http://localhost:8089` and set:

- **Number of users** — peak concurrent users to simulate
- **Ramp up** — users spawned per second
- **Run time** — optional, e.g. `5m`

### Headless mode (for CI/automation)

No browser UI — runs for a fixed duration and writes reports automatically:

```bash
locust -f stresswatch.py --host https://your-internal-service.company.com \
    --users 50 --spawn-rate 5 --run-time 5m --headless \
    --html report.html --csv results
```

This produces `report.html` (visual summary) and `results_*.csv` (raw stats), ready to archive as CI artifacts or attach to a performance report.

---

## Customizing for Your Target

This script is a template — edit it to match the service you're testing:

1. **Update the task endpoints** (`view_homepage`, `view_product`, `search`, `submit_form`) to match your actual API routes
2. **Add authentication** in `on_start()` if your service requires login — there's a commented example showing how to authenticate once per simulated user and store a session token
3. **Adjust task weights** (`@task(N)`) to reflect your real traffic distribution
4. **Adjust `wait_time`** if your users interact faster or slower than the 1–3 second default

---

## Event Hooks

| Hook | What it does |
|---|---|
| `on_request` | Logs any failed request, and flags requests slower than 2000ms as they happen |
| `on_test_start` | Prints a reminder to monitor server-side CPU/memory/error rates once the test begins |
| `on_test_stop` | Prints a reminder to check the generated report/CSV files |

These give you real-time visibility in the terminal alongside the Locust web UI or headless summary.

---

## Reading Results

- **Response time percentiles** (p50/p95/p99 in the Locust UI or CSV) matter more than averages — a high p99 means some users are having a bad experience even if the average looks fine
- **Failure rate** climbing as user count increases usually marks where the service starts to buckle
- **Slow request logs** (from the `on_request` hook) point to specific endpoints worth investigating first
- Cross-reference with server-side metrics (CPU, memory, DB connections, error logs) during the same time window — client-side numbers alone don't tell you *why* something slowed down

---

## Limitations

- Simulates HTTP traffic only — no browser rendering, so client-side JS performance isn't measured
- Task behavior is scripted and weighted, not a perfect model of real user behavior
- Authentication, session handling, and realistic payloads need to be added per-target (see commented example in `on_start()`)

---

## Authorized Use Only

This tool generates real load against the target it's pointed at. **Only run it against services you own or have explicit written authorization to load-test.** Running it against third-party or production systems without permission can cause outages, violate terms of service, and may be illegal. Always coordinate load tests with the team responsible for the target service, and avoid running them against production without a planned maintenance window unless specifically testing production capacity with sign-off.

---

## Author

**Oladunni Oluwaseyi**
GitHub: [@oluwaseyi-rgb](https://github.com/oluwaseyi-rgb)
LinkedIn: [Oluwaseyi Oladunni](https://www.linkedin.com/in/oluwaseyi-oladunni-6a42b1407)

---

## License

Released under the MIT License.
