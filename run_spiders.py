import argparse
import logging
import os
from datetime import date, datetime
from typing import List, Optional, Tuple

from dateutil import relativedelta
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from planning_applications.db import get_earliest_date_for_lpa
from planning_applications.settings import DEFAULT_DATE_FORMAT

logger = logging.getLogger(__name__)


def get_spider_names() -> List[str]:
    spider_names = []
    spiders_dir = "planning_applications/spiders/lpas"

    # Skip __init__.py and get all .py files
    for file in os.listdir(spiders_dir):
        if file.endswith(".py") and file != "__init__.py":
            spider_name = file[:-3]  # Remove .py extension
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

    for spider_name in spider_names:
        spider_kwargs = {}

        if lpa_dates:
            lpa_config = next((x for x in lpa_dates if x[0] == spider_name), None)
            if lpa_config:
                spider_kwargs["start_date"] = lpa_config[1].strftime(DEFAULT_DATE_FORMAT)
                spider_kwargs["end_date"] = lpa_config[2].strftime(DEFAULT_DATE_FORMAT)
                logger.info(f"Adding spider {spider_name} with dates {lpa_config[1]} to {lpa_config[2]}")
            else:
                logger.info(f"Skipping spider {spider_name} - not in LPA dates list")
                continue
        elif from_earliest:
            earliest_date = get_earliest_date_for_lpa(spider_name)
            if earliest_date:
                logger.info(f"Earliest date on record for {spider_name} is {earliest_date}")

                start_date = earliest_date + relativedelta.relativedelta(months=1)
                candidate_end_date = start_date + relativedelta.relativedelta(months=1)
                end_date = candidate_end_date if candidate_end_date >= date.today() else date.today()

                spider_kwargs["start_date"] = start_date.strftime(DEFAULT_DATE_FORMAT)
                spider_kwargs["end_date"] = end_date.strftime(DEFAULT_DATE_FORMAT)
            else:
                logger.info(f"No earliest date on record for {spider_name}. Using most recent month")

                start_date = date.today() - relativedelta.relativedelta(months=1)
                end_date = date.today()

                spider_kwargs["start_date"] = start_date.strftime(DEFAULT_DATE_FORMAT)
                spider_kwargs["end_date"] = end_date.strftime(DEFAULT_DATE_FORMAT)

            logger.info(f"Adding spider {spider_name} with dates {start_date} to {end_date}")
        else:
            logger.info(f"Adding spider {spider_name} with default dates")

        process.crawl(spider_name, **spider_kwargs)

    logger.info("Starting crawl process...")
    process.start()


def main():
    parser = argparse.ArgumentParser(description="Run planning application spiders")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--from-earliest",
        action="store_true",
        help="Start from earliest date in database plus one month for all spiders",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all spiders with default dates",
    )
    group.add_argument(
        "--lpa-dates",
        nargs="+",
        help="List of LPA,start_date,end_date (e.g., 'cambridge,2024-01-01,2024-02-01')",
    )
    group.add_argument(
        "--lpas-from-earliest",
        nargs="+",
        help="List of LPA names to run from their earliest dates (e.g., 'cambridge barnet')",
    )

    args = parser.parse_args()
    all_spider_names = get_spider_names()

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
