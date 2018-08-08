import schedule
import time
from app.management.commands.export_results import Command as ExportResultsCommand
from app.management.commands.set_caches import Command as SetCachesCommand
from app.management.commands.resolve_countries import Command as ResolveCountriesCommand
from app.management.commands.set_attributes import Command as SetAttributesCommand

# Daily jobs
schedule.every(1).days.do(ExportResultsCommand().handle())
schedule.every(1).days.do(SetCachesCommand().handle())
schedule.every(1).days.do(ResolveCountriesCommand().handle())

# Hourly jobs
schedule.every(12).hour.do(SetAttributesCommand().handle())


def main():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()