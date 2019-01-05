import schedule
import time


def command_callable(command):
    return command().handle


# Weekly jobs

from app.management.commands.export_results import Command
schedule.every(7).days.do(command_callable(Command))

from app.management.commands.set_caches import Command
schedule.every(7).days.do(command_callable(Command))

from app.management.commands.resolve_countries import Command
schedule.every(7).days.do(command_callable(Command))

# Hourly jobs

from app.management.commands.set_attributes import Command
schedule.every(4).hours.do(command_callable(Command))


def main():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
