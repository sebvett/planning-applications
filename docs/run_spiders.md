# `run_spiders.py` Usage Guide

This document outlines how to use the `run_spiders.py` script, an alternative to calling `scrapy` directly.

## Commands

The script provides two main commands:

### 1. LPA Planning Applications

```bash
uv run run_spiders.py lpas [options]
```

Before running the script, you'll see a summary table displaying the name of each spider, the mode (LPA Dates or From Earliest), earliest date on record, start date, and end date.

#### Options

- `--all`: Run all working spiders with default dates (skips spiders marked as not working)
- `--from-earliest`: Start from earliest date in database plus one month for all spiders
- `--lpa-dates LPA,START_DATE,END_DATE [LPA,START_DATE,END_DATE ...]`: Run specific LPAs with custom date ranges
  - Example: `--lpa-dates "cambridge,2024-01-01,2024-02-01" "barnet,2024-01-15,2024-02-15"`
- `--lpas-from-earliest LPA [LPA ...]`: Run specific LPAs from their earliest dates in the database
  - Example: `--lpas-from-earliest cambridge barnet`

### 2. Planning Appeals

```bash
uv run run_spiders.py appeals --from-date YYYY-MM-DD --to-date YYYY-MM-DD
```

#### Required Arguments

- `--from-date`: Start date for appeals data collection (inclusive, format YYYY-MM-DD)
- `--to-date`: End date for appeals data collection (inclusive, format YYYY-MM-DD)

## Examples

### Run all working LPAs

```bash
uv run run_spiders.py lpas --all
```

### Run specific LPAs with custom date ranges

```bash
uv run run_spiders.py lpas --lpa-dates "cambridge,2024-01-01,2024-02-01" "oxford,2024-01-15,2024-02-15"
```

### Run specific LPAs from their earliest dates in the database

```bash
uv run run_spiders.py lpas --lpas-from-earliest cambridge oxford
```

### Run appeals spider for a specific date range

```bash
uv run run_spiders.py appeals --from-date 2024-01-01 --to-date 2024-02-01
```
