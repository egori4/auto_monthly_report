# Auto Monthly Report

Automated security reporting tool for **Radware DefensePro / Vision or CyberController** environments. Collects attack and traffic data via the Vision REST API, processes it with Python, and generates interactive HTML trend reports and PDF summaries — delivered by email on a scheduled basis.

Reports cover monthly and daily timeframes and include charts for attack events, malicious bandwidth/packets, traffic utilization, top source IPs, top policies, top attacked destinations, device breakdown, and more — all rendered with Google Charts and backed by SQLite.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Option 1 — Docker (Recommended)](#option-1--docker-recommended)
  - [Option 2 — Linux or WSL](#option-2--linux-or-wsl)
- [Configuration](#configuration)
  - [customers.json](#customersjson)
  - [run.sh Variables](#runsh-variables)
- [Usage](#usage)
  - [Monthly Report](#monthly-report)
  - [Daily Report](#daily-report)
  - [Convert Forensics File to SQLite](#convert-forensics-file-to-sqlite)
- [Project Structure](#project-structure)
- [Updating to a New Version](#updating-to-a-new-version)
- [Uninstalling](#uninstalling)
- [Roadmap](#roadmap)
- [Changelog](#changelog)

---

## Features

- **Monthly & daily report modes** — separate pipelines and HTML outputs for each
- **Interactive HTML reports** — Google Charts with stacked/non-stacked toggle, category checkboxes, and check/uncheck-all controls
- **PDF report generation** — compiled via PHP
- **Traffic utilization charts** — BPS, PPS, CPS, CEC per device, with granular and averaged windows
- **Attack analysis** — events, malicious bandwidth, malicious packets, top attacks, top source IPs, top policies, top attacked destinations
- **Trend analysis** — multi-month historical trends across all metrics
- **AbuseIPDB integration** — optional enrichment of top malicious IPs with abuse scores
- **Policy filtering** — configurable allow-list of policies to include in reports
- **Forensics-to-SQLite converter** — import offline forensics CSV exports into the database
- **Configurable units** — per-customer Gbps/Mbps/Tbps and Millions/Billions/Thousands packet units
- **Email delivery** — SMTP with optional proxy and authentication
- **Docker deployment** — runs as a container on Vision or any Linux host
- **Automatic file retention** — configurable cleanup of reports older than N months

---

## How It Works

```
Vision API
    |
    v
collector.py          <-- pulls forensics + traffic stats into SQLite & CSV
    |
    v
charts_and_tables.py  <-- aggregates data, produces chart-ready CSV files
    |
    +---> analyze_trends.py       <-- builds monthly HTML trend report
    +---> analyze_trends_daily.py <-- builds daily HTML trend report
               |
               v
          email_send.py     <-- attaches HTML + PDF and sends via SMTP
```
The entry points are `run.sh` (monthly) and `run_daily.sh` (daily). Each step is individually toggleable via boolean flags in those scripts.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.x | With `pip` |
| `pandas`, `requests` | `pip install -r requirements.txt` |
| Docker (optional) | For containerized deployment |
| Bash | Linux, macOS, or Windows WSL |

---

## Installation

### Option 1 — Docker (Recommended)

Deploying as a Docker container is the recommended approach, especially when running on a Vision server where you want the script to survive future Vision upgrades.

**1. SSH into the Vision server as root and copy the installation package:**

```bash
cd /tmp
curl -o radware_report.tar.gz https://filepile.radware.com/files/download/f98-137-a0b -k -L --progress-bar
```

**2. Create the persistent script directory:**

```bash
mkdir -p /opt/radware/storage/scripts/radware_report
```

**3. Extract the package:**

```bash
tar -zxvf /tmp/radware_report.tar.gz -C /opt/radware/storage/scripts/radware_report
```

**4. Navigate to the directory:**

```bash
cd /opt/radware/storage/scripts/radware_report
```

**5. (Optional) Edit `install.sh` to adjust the cron schedule:**

```bash
vi install.sh
```

**6. Run the installer:**

```bash
./install.sh
```

**7. Verify the container was created:**

```bash
docker ps -a
# Expect a line for radware_report with an empty STATUS
```

**8. Configure the script** — see [Configuration](#configuration) below.

**9. Run manually (without waiting for cron):**

```bash
docker start radware_report
docker start -i radware_report   # interactive, shows live output
```

**10. Verify successful completion:**

```bash
docker ps -a
# STATUS should show: Exited (0)
```

**11. Check logs if the exit code is not 0:**

```bash
docker logs radware_report
```

---

### Option 2 — Linux or WSL

**Install WSL on Windows 10/11** (if needed):
- [Official WSL install guide](https://docs.microsoft.com/en-us/windows/wsl/install)

**Install PHP dependencies:**

```bash
sudo apt install php7.4-cli php7.4-curl php7.4-sqlite3
```

**Install Python dependencies:**

```bash
sudo apt-get update
sudo apt install python3-pip
pip install -r requirements.txt
```

**Run the script:**

```bash
cd app
./run.sh
```

> Make sure `run.sh` is executable: `chmod +x run.sh`

---

## Configuration

### customers.json

Copy the example file and edit it:

```bash
cp config_files/customers_example.json config_files/customers.json
vi config_files/customers.json
```

**Required fields:**

| Key | Description |
|---|---|
| `id` | Customer ID — must match `cust_id` in `run.sh`. No underscores. |
| `longName` | Full display name used in reports |
| `ip` | Vision server IP address |
| `dps` | Comma-separated list of DefensePro IPs |
| `defensepros` | Object mapping DefensePro IP -> device name |
| `user` | Vision login username |
| `pass` | Vision login password |
| `exclude` | List of attack categories to exclude from reports |
| `policiesList` | List of policy names to include, e.g. `["policy-a", "policy-b"]` |

**Optional `variables` section:**

| Key | Default | Description |
|---|---|---|
| `bwUnit` | `"Gigabytes"` | Monthly bandwidth unit: `"Megabytes"`, `"Gigabytes"`, `"Terabytes"` |
| `pktUnit` | `"Millions"` | Monthly packet unit: `"Millions"`, `"Billions"`, `"Thousands"`, `"As is"` |
| `bwUnitDaily` | `"Gigabytes"` | Daily bandwidth unit (also controls BPS display as Mbps or Gbps) |
| `pktUnitDaily` | `"Millions"` | Daily packet unit |
| `TrafficWindow` | `3600` | Seconds per API call window for traffic collection |
| `ForensicsWindow` | `3600` | Seconds per API call window for forensics collection |
| `TrafficWindowGranular` | `86400` | Granular traffic window in seconds |
| `TrafficWindowAveraged` | `14400` | Averaged traffic window in seconds |
| `PreAttackTimestampsToKeep` | `1` | Extra minutes of granular data before attack |
| `PostAttackTimestampsToKeep` | `5` | Extra minutes of granular data after attack |
| `barChartsAnnotations` | `"true"` | Show callout annotations on bar charts |

---

### run.sh Variables

Copy the example and edit it:

```bash
cp run_example.sh run.sh
chmod +x run.sh
vi run.sh
```

**Key variables:**

```bash
cust_list=(Customer-name)           # Space-separated customer IDs (no underscores)

abuseipdb=true                      # Enable AbuseIPDB enrichment
abuseipdb_key="your-api-key"        # From https://www.abuseipdb.com/account/api

delete_old_files_retention=6        # Months of reports to retain
top_n=7                             # Top N items shown in charts/tables

smtp_server="smtp.example.com"
smtp_server_port=25
smtp_sender="sender@example.com"
smtp_password="password"
smtp_list=(user1@mail.com user2@mail.com)

# Toggle pipeline steps on/off:
del_old_files=true
collect_data=true
gen_python_csv_data=true
modify_csv=true
generate_report=true
generate_appendix=true
analyze_trends=true
email_send=true
```

> **Note:** `run_daily.sh` has the same structure. Keep both files in sync when adding new variables from release notes.

---

## Usage

### Monthly Report

```bash
./run.sh
```

Generates a monthly PDF report and an interactive HTML trends file for the previous month. Output is placed in `report_files/<cust_id>/`.

### Daily Report

```bash
./run_daily.sh
```

Generates a daily HTML report appending the current day's data to the monthly database.

### Convert Forensics File to SQLite

When you have an offline forensics export, you can convert it to a SQLite database for use in report generation.

**1. Place the forensics CSV under:**

```
database_files/<cust_id>/1_week_2023-11-27_15-53-20.csv
```

**2. Set the following variables in `run.sh`:**

```bash
convert_forensics_to_sqlite=true
forensics_file_cust_id="CUSTID"
forensics_date_format="%m.%d.%Y %I:%M:%S %p"
forensics_file_name="1_week_2023-11-27_15-53-20.csv"
converted_sqlite_file_name="database_CUSTID_10.sqlite"
```

> Supported date formats:
> - `%m.%d.%Y %I:%M:%S %p` — 12-hour clock
> - `%m.%d.%Y %H:%M:%S` — 24-hour clock
> - `%d.%m.%Y %I:%M:%S %p` — day-first, 12-hour
> - `%d.%m.%Y %H:%M:%S` — day-first, 24-hour
>
> If the date includes a timezone string (e.g., `04.03.2024 8:00:11 PM EDT`), remove the timezone suffix from the CSV first.

**3. Run:**

```bash
./run.sh
```

---

## Project Structure

```
auto_monthly_report/
  run_example.sh              # Monthly report orchestrator (copy -> run.sh)
  run_daily_example.sh        # Daily report orchestrator (copy -> run_daily.sh)
  requirements.txt            # Python dependencies
  config_files/
    customers.json            # Per-customer configuration
  script_files/
    collector.py              # Vision API data collection
    charts_and_tables.py      # Monthly CSV aggregation
    charts_and_tables_daily.py
    analyze_trends.py         # Monthly HTML report generator
    analyze_trends_daily.py   # Daily HTML report generator
    forensics_to_sqlite.py    # Forensics CSV -> SQLite converter
    email_send.py             # Monthly email delivery
    email_send_daily.py       # Daily email delivery
    abuseipdb.py              # AbuseIPDB API integration
    delete_column_csv.py      # CSV post-processing (removes outliers)
    del_old_files.py          # File retention cleanup
    data_parser_to_appendix.py
  database_files/             # SQLite databases per customer
  source_files/               # Raw collected data
  report_files/               # Generated reports (PDF, HTML)
  raw_data_files/             # Intermediate processing files
  tmp_files/                  # Temporary working files
  log/                        # Execution logs
  Container/                  # Docker deployment assets
```

**SQLite naming convention:** `database_<CUST_ID>_<MM>_<YYYY>.sqlite`

> **Tip:** To backfill historical trend data, copy an existing database for a prior month into `database_files/<cust_id>/` using the naming convention above. The next run will automatically incorporate it.

---

## Updating to a New Version

```bash
# Replace the app directory with the latest from GitHub
git pull   # or download and extract the archive

# Ensure scripts are executable
chmod +x run.sh run_daily.sh

# Review release notes below for any new required variables in:
#   - run.sh / run_daily.sh
#   - config_files/customers.json
```

> Always diff your `run.sh` against `run_example.sh` after an update to pick up new variables.

---

## Uninstalling

**Docker:**

```bash
. /opt/radware/storage/scripts/radware_report/uninstall.sh
rm -rf /opt/radware/storage/scripts/radware_report
```

---

## Roadmap

- Move device distribution chart from monthly to daily report
- Display version number in generated HTML reports
- Backup traffic utilization stats at the start of each new month instead of overwriting
- High-level management summary report (text-based, mirroring email body)
- License threshold monitoring with alerts when traffic approaches the limit
- MAX daily BPS/PPS/CEC/CPS graph per day
- Indicate different sampling rates (15-second vs. 5-minute) with a note in the chart
- Timezone handling for daily report traffic utilization (data collected in UTC, displayed in local time)

---

## Changelog


### V11.12.4 (8/12/2026)
- Added logic if device was skipped due to no data and no column was created for this device, when the device is recovered, the column will be created for it

### V11.12.3 (7/16/2026)
- Added logic to skip devices with no available traffic stats from traffic charts

### V11.12.2 (7/18/2025)
- Fixed script failure when a non-existent DefensePro is added to the config

### V11.12.1 (7/7/2025)
- Fixed wrong indexing in Table of Contents

### V11.12 (6/24/2025)
- Added new charts: Top Attacked Destinations

### V11.11 (5/5/2025)
- Monthly/Daily: added filter-by-policy feature
  > **Migration:** Add `"policiesList": ["policy-a","policy-b"]` to `config_files/customers.json`

### V11.10.6
- Daily report: migrated Traffic BPS/PPS/CPS/CEC storage from CSV to SQLite
  > **Migration:** Recollect last month's data or start fresh on the 2nd of the month

### V11.10.5
- Added check-all / uncheck-all checkbox controls to charts

### V11.10.4 (5/15/2025)
- `collector.py`: workaround for events where `end date` is earlier than `start date`

### V11.10.3 (5/5/2025)
- Monthly report: corrected overly dark section headers to white

### V11.10.2 (4/1/2025)
- Monthly report: fixed "Attack distribution" button returning N/A
- Monthly report: changed packet/bandwidth units from integer to float to avoid zero values on small counts
- Monthly report: typo fixes and extra room for "Total Attack Time in days" annotations

### V11.10.1 (3/31/2025)
- Monthly report: ported chart color persistence (check/uncheck) from daily report
- Monthly report: fixed expandable table header text color and button alignment

### V11.10 (3/28/2025)
- `collector.py`: added `TrafficWindowGranular`, `TrafficWindowAveraged`, `PreAttackTimestampsToKeep`, `PostAttackTimestampsToKeep` variables
  > **Migration:** Add these keys to `customers.json`
- Daily report: merged traffic and attacks onto a single combined chart
- Daily report: added chart color persistence on check/uncheck
- Daily report: renamed "malicious bandwidth/packets" to "Attack Volume / Attack Packets"
- Daily report: added Excluded Traffic (Mbps) and Excluded Traffic (PPS) charts

### V11.9.2 (3/11/2025)
- Daily report: print success/error status after email send

### V11.9.1
- Headline color improvements (separate branch)

### V11.9 (3/7/2025)
- Monthly report: removed all daily charts; added Table of Contents, top banner, and "Back to Top" button
- Monthly/Daily: renamed "Back to TOC" button to "Back to Top"
- Fixed `FutureWarning` for deprecated `df.applymap` -> `df.apply`

### V11.8.1 (3/5/2025)
- "Back to Top" button now scrolls to page top instead of TOC anchor
- Fixed decimal display on X-axis in cumulative bandwidth breakdown chart
- Added X/Y axis titles; unified "security events" terminology

### V11.8 (3/4/2025)
- Added header image and repositioned page title
- Added headlines, renamed and restructured charts
- Added Table of Contents and floating "Back to TOC" button

### V11.7 (3/3/2025)
- Added CEC/PPS attack charts
- Categorized charts into BPS/PPS sections
- Added 403 error handling and re-authentication logic
- Code optimization pass

### V11.6 (2/27/2025)
- PHP files cleanup

### V11.5.1 (2/27/2025)
- Fixed CPS device chart checkbox selection
- Removed "combined" from BPS, Attacks, and CPS chart titles

### V11.5 (2/26/2025)
- Subtracted attack traffic from total to show clean legitimate traffic in top chart
- Aggregated non-attack timestamps
- Added Connections Per Second (CPS) collection and chart

### V11.4 (2/20/2025)
- Added `TrafficWindow` and `ForensicsWindow` variables to `customers.json`
  > **Migration:** Add `"TrafficWindow"` and `"ForensicsWindow"` under `"variables"` in `customers.json`

### V11.3 (2/19/2025)
- Removed incomplete timestamps from traffic volume data to prevent chart gaps
- Changed traffic volume chart color scheme to shades of blue

### V11.2 (2/18/2025)
- Traffic volume collection now uses 1-hour windows for better granularity

### V11.1 (2/15/2025)
- Rebuilt data collection using time-range chunking instead of pagination
- New traffic utilization per-device combined chart
- New attacks per-device combined chart

### V11.0 (12/30/2024)
- Replaced PHP-based collection with Python (`collector.py`) for traffic utilization and forensics
  > **Migration:** Update `run.sh` and `run_daily.sh` from examples; rename SQLite files to include year — e.g., `database_EA_12.sqlite` -> `database_EA_04_2024.sqlite`

### V10.3.4 (2/4/2025)
- Added `barChartsAnnotations` variable to `customers.json`
  > **Migration:** Add `"barChartsAnnotations": "true"` under `"variables"` in `customers.json`
- Limited device bar charts to Top N devices only

### V10.3.3 (1/31/2025)
- Dynamic max-value calculation for bar chart annotation headroom
- Source IP packet units changed to None

### V10.3.2 (1/31/2025)
- Traffic utilization: added Y and X axis legends
- Bar chart callouts moved outside bars; bars made narrower
- Fixed device bar chart bandwidth values
- Added DefensePro IP -> device name translation for bar charts
- "Total Attack Time in Days" chart: resized, centered, minimum set to 0, callouts outside

### V10.3.1 (1/14/2025)
- Removed units from chart titles; added axis descriptions
- Added annotation callouts to bar charts
- Added 3 new bar charts: events, packets, bandwidth by device this month

### V10.3 (1/13/2025)
- Minor grammatical corrections to email body
- Added "Total Attack Time in Days" chart

### V10.2 (11/19/2024)
- Monthly report: moved detailed data tables behind expandable buttons (matching daily report)

### V10.1 (11/13/2024)
- Daily report: moved detailed data tables behind expandable buttons
- Daily report: changed all charts from stacked to non-stacked by default

### V10.0 (10/21/2024)
- Added user-configurable chart options: stacked/non-stacked toggle, category select/deselect
- Improved chart tooltip to show all categories on mouse hover

### V9.8.0 (10/4/2024)
- Fixed crash when a removed device still has data in the database
- Added option to exclude specific device information from reports

### V9.7.2 (7/10/2024)
- Fixed missing `elif` for `"as is"` packet unit in daily report
- Fixed typo in daily report email subject

### V9.7.1 (7/5/2024)
- Fixed monthly report "Malicious bandwidth per day" chart units bug

### V9.7 (7/5/2024)
- BPS unit now auto-derived from `bwUnitDaily`: `"Megabytes"` -> Mbps; `"Gigabytes"`/`"Terabytes"` -> Gbps

### V9.6 (6/19/2024)
- New charts: Max PPS and Max BPS daily distribution (daily and monthly)
- Fixed traffic utilization chart and daily packets chart
- `charts_and_tables_daily.py`: bandwidth/packet unit optimizations

### V9.5 (6/12/2024)
- `forensics_to_sqlite.py`: added user-configurable `forensics_date_format`
  > **Migration:** Add `"forensics_date_format"` and `"db_from_forensics"` to `run.sh`

### V9.4 (6/12/2024)
- Added `bw_units_sum` variable
- Added configurable `abuseipdb` toggle (true/false) in `run.sh` and `run_daily.sh`
  > **Migration:** Add `abuseipdb` variable to `run.sh` and `run_daily.sh`
- Fixed "Top Attacks and Policies for Devices" table
- Fixed units in table to match `customers.json` configuration

### V9.3.5 (4/4/2024)
- Exported `durationRange` as `Duration Range` to CSV database

### V9.3.4 (2/27/2024)
- Fixed corner case where a numeric policy name was incorrectly cast to integer, breaking JavaScript

### V9.3.3 (2/12/2024)
- Renamed HTML output files: `trends-daily_<CUST>_<MM>_<YYYY>.html` and `trends-monthly_<CUST>_<MM>_<YYYY>.html`

### V9.3.2 (2/12/2024)
- Auto-create `report_files/<cust_id>/` if missing
- Monthly report cosmetic improvements (column renames: Count -> Security Events, deviceName -> Device Name, etc.)

### V9.3.1 (1/29/2024)
- Introduced `bwUnitDaily` and `pktUnitDaily` in `customers.json`
  > **Migration:** Add `"bwUnitDaily"` and `"pktUnitDaily"` to `customers.json`

### V9.3 (1/26/2024)
- Units are now configurable per customer in `customers.json`
  > **Migration:** Add `bwUnit`, `pktUnit` to `customers.json` and update `run.sh`/`run_example.sh`

### V9.2.2 (1/25/2024)
- Various bugfixes in `run.sh`, `run_daily_example.sh`
- `abuseipdb.py`: improved communication error logging
- `analyze_trends_daily.py`: aligned charts to full page width; column rename improvements

### V9.2.1 (1/17/2024)
- Fixed January email bug in `run_daily_example.sh`
- Fixed top source IP by packets flat chart
- Fixed "Total" column calculation for first-day events in daily tables

### V9.2 (12/29/2023)
- Disabled `InsecureRequestWarning` in `abuseipdb.py`
- Added table cell top-alignment in `analyze_trends.py`
- Fixed daily path reference (run_daily.sh)
- Added `email_send_daily.py`
- Added `delete_column_csv.py` for removing specific data from CSV

### V9.1 (12/13/2023)
- Fixed daily email sending the previous month's files instead of current month's

### V9.0 (12/12/2023)
- New feature: daily data collection and reporting
  > **Migration:** Update `run.sh` from `run_example.sh`
- `analyze_trends_daily.py` and `analyze_trends.py`: added CSV export
- `email_send.py`: fixed duplicate archiving when file was already archived

### V8.0 (12/4/2023)
- New feature: create SQLite database from forensics file
  > **Migration:** Update `run.sh`
- `email_send.py`: added EA case handling
- `analyze_trends.py`: graceful handling when previous month data is unavailable
- `charts_and_tables.py`: skip traffic stats if SQLite was built from forensics
- `CollectAll.php`: auto-create `source_files` and `database_files` directories

### V7.3.1 (11/21/2023)
- New charts and tables: Events per day, Malicious bandwidth per day, Malicious packets per day (last month)
- Traffic utilization chart: added hour and minute to scale
- Added month and year to report headline

### V7.3 (11/20/2023)
- New feature: Traffic utilization last month chart
  > **Migration:** Update `run.sh` from example

### V7.2.1 (11/17/2023)
- Moved `pkt_units` and `bw_units` from `analyze_trends.py` to `run.sh`
  > **Migration:** Update `run.sh` from example

### V7.2 (11/16/2023)
- Fixed Top Source IP by packet count division and AbuseIPDB score
- New feature: additional drill-down tables below charts

### V7.1 (11/7/2023)
- `analyze_trends.py`: added report title
- Added three "All-Time High" TopN charts

### V7.0.9 (10/24/2023)
- Added `"Thousands"` as a packet unit option

### V7.0.8 (10/12/2023)
- Disabled PDF zipping in `report.php`

### V7.0.7 (10/11/2023)
- Fixed table names, phrasing, and grammar

### V7.0.6 (9/20/2023)
- `analyze_trends.py`: added percentage calculations to trend data
- `abuseipdb.py`: updated health check endpoint

### V7.0.5 (9/7/2023)
- Excluded report HTML and TXT files from email attachments

### V7.0.4 (9/5/2023)
- Added top policies charts and tables to trends analysis
- Fixed bandwidth and packet unit labels in PDF

### V7.0.3 (8/31/2023)
- Added top source IP charts and tables to trends analysis

### V7.0.2 (8/29/2023)
- Trends analysis: added 6 summary tables; added `isStacked` parameter to area charts

### V7.0.1 (8/28/2023)
- Trends analysis: added 3 new charts — events, packets, and bandwidth per device

### V7.0 (8/24/2023)
- Initial Git release
- Added automated trends analysis HTML generation
- Fixed recursive directory removal in `del_old_files.py`
- Script supports Linux, WSL, and Docker container deployment
