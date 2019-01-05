import schedule
import time


def command_callable(command):
    return command.handle


# Weekly jobs

from app.management.commands.export_results import ExportResults as Command
command_callable(Command)
schedule.every(7).days.do(command_callable(Command))

from app.management.commands.set_caches import SetCachesCommand as Command
command_callable(Command)
schedule.every(7).days.do(command_callable(Command))

from app.management.commands.resolve_countries import ResolveCountriesCommand as Command
command_callable(Command)
schedule.every(7).days.do(command_callable(Command))

# # Hourly jobs

from app.management.commands.set_attributes import SetAttributesCommand as Command
command_callable(Command)
schedule.every(4).hours.do(command_callable(Command))


def main():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
