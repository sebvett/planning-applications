import argparse
import logging
import os
from datetime import date, datetime
from typing import List, Optional, Tuple

from dateutil import relativedelta
from rich.console import Console
from rich.table import Table
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from planning_applications.db import get_earliest_date_for_lpa
from planning_applications.settings import DEFAULT_DATE_FORMAT

logger = logging.getLogger(__name__)


def get_spider_names(skip_not_working: bool = False) -> List[str]:
    spider_names = []
    spiders_dir = "planning_applications/spiders/lpas"

    # Skip __init__.py and get all .py files
    for file in os.listdir(spiders_dir):
        if file.endswith(".py") and file != "__init__.py":
            spider_name = file[:-3]  # Remove .py extension
        if skip_not_working:
            module = __import__(f"planning_applications.spiders.lpas.{spider_name}", fromlist=["*"])
            spider_class = next(
                (cls for name, cls in module.__dict__.items() if isinstance(cls, type) and name.endswith("Spider")),
                None,
            )
            if spider_class and getattr(spider_class, "not_yet_working", False):
                continue
        spider_names.append(spider_name)

    return sorted(spider_names)


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, DEFAULT_DATE_FORMAT).date()


def parse_lpa_dates(lpa_dates: List[str]) -> List[Tuple[str, date, date]]:
    """Parse list of lpa,start_date,end_date strings."""
    result = []
    today = date.today()

    for lpa_date in lpa_dates:
        try:
            lpa, start, end = lpa_date.split(",")
            start_date = parse_date(start)
            end_date = parse_date(end)

            if start_date > end_date:
                logger.warning(f"Start date {start_date} is in the future for LPA {lpa}, adjusting to {today}")
                start_date = today

            if start_date > date.today():
                logger.error(f"Start date {start_date} is in the future for LPA {lpa}")
                continue

            result.append((lpa, start_date, end_date))
        except ValueError as e:
            raise ValueError(f"Invalid lpa,start_date,end_date format: {lpa_date}. Error: {e}")
    return result


def run_spiders(
    spider_names: List[str],
    from_earliest: bool = False,
    lpa_dates: Optional[List[Tuple[str, date, date]]] = None,
) -> None:
    """Run multiple spiders using CrawlerProcess."""
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    spider_dates = []

    for spider_name in spider_names:
        spider_kwargs = {}

        if lpa_dates:
            lpa_config = next((x for x in lpa_dates if x[0] == spider_name), None)
            if lpa_config:
                mode = "LPA Dates"
                start_date_dt = lpa_config[1]
                end_date_dt = lpa_config[2]
                spider_kwargs["start_date"] = start_date_dt.strftime(DEFAULT_DATE_FORMAT)
                spider_kwargs["end_date"] = end_date_dt.strftime(DEFAULT_DATE_FORMAT)

                logger.info(f"Adding spider {spider_name} with dates {start_date_dt} to {end_date_dt}")
            else:
                logger.info(f"Skipping spider {spider_name} - not in LPA dates list")
                continue
        elif from_earliest:
            earliest_date = get_earliest_date_for_lpa(spider_name)
            if earliest_date:
                mode = "From Earliest"
                logger.info(f"Earliest date on record for {spider_name} is {earliest_date}")

                start_date_dt = min(earliest_date + relativedelta.relativedelta(months=1), date.today())
                end_date_dt = min(start_date_dt + relativedelta.relativedelta(weeks=1), date.today())

                spider_kwargs["start_date"] = start_date_dt.strftime(DEFAULT_DATE_FORMAT)
                spider_kwargs["end_date"] = end_date_dt.strftime(DEFAULT_DATE_FORMAT)

                logger.info(f"Adding spider {spider_name} with dates {start_date_dt} to {end_date_dt}")
            else:
                mode = "From Earliest (Default)"

                logger.info(f"No earliest date on record for {spider_name}. Using most recent month")

                start_date_dt = date.today() - relativedelta.relativedelta(weeks=1)
                end_date_dt = date.today()

                spider_kwargs["start_date"] = start_date_dt.strftime(DEFAULT_DATE_FORMAT)
                spider_kwargs["end_date"] = end_date_dt.strftime(DEFAULT_DATE_FORMAT)

                logger.info(f"Adding spider {spider_name} with dates {start_date_dt} to {end_date_dt}")
        else:
            logger.info(f"No option passed. Skipping spider {spider_name}")
            continue

        spider_dates.append((spider_name, mode, str(earliest_date), str(start_date_dt), str(end_date_dt)))
        process.crawl(spider_name, **spider_kwargs)

    table = Table(title="Spider Dates Summary")
    table.add_column("Spider", style="cyan")
    table.add_column("Mode", style="magenta", justify="center")
    table.add_column("Earliest Date on Record", style="green", justify="center")
    table.add_column("Start Date", justify="center")
    table.add_column("End Date", justify="center")
    for name, mode, earliest_date, start, end in spider_dates:
        table.add_row(name, mode, earliest_date, start, end)

    console = Console()
    console.print(table)

    logger.info("Starting crawl process...")
    process.start()


def main():
    parser = argparse.ArgumentParser(description="Run planning application spiders")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all working spiders with default dates",
    )
    parser.add_argument(
        "--from-earliest",
        action="store_true",
        help="Start from earliest date in database plus one month for all spiders",
    )
    parser.add_argument(
        "--lpa-dates",
        nargs="+",
        help="List of LPA,start_date,end_date (e.g., 'cambridge,2024-01-01,2024-02-01')",
    )
    parser.add_argument(
        "--lpas-from-earliest",
        nargs="+",
        help="List of LPA names to run from their earliest dates (e.g., 'cambridge barnet')",
    )
    args = parser.parse_args()

    all_spider_names = get_spider_names(skip_not_working=args.all)

    if args.lpas_from_earliest:
        invalid_lpas = [lpa for lpa in args.lpas_from_earliest if lpa not in all_spider_names]
        if invalid_lpas:
            logger.error(f"Error: Invalid LPA names: {', '.join(invalid_lpas)}")
            return
        run_spiders(args.lpas_from_earliest, from_earliest=True)
    elif args.lpa_dates:
        lpa_dates = parse_lpa_dates(args.lpa_dates)
        run_spiders(all_spider_names, lpa_dates=lpa_dates)
    else:
        run_spiders(all_spider_names, from_earliest=args.from_earliest)


if __name__ == "__main__":
    main()
