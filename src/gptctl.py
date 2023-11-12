import argparse
from src.commands.assistant import AssistantCommand
from src.commands.thread import ThreadCommand
from src.commands.files import FileCommand
from src.utils.context import Context

COMMANDS = [
    {
        "name": "assistant",
        'instance': AssistantCommand(),
    },
    {
        "name": "thread",
        'instance': ThreadCommand(),
    },
    {
        "name": "file",
        'instance': FileCommand(),
    },
]


def main():
    # init parser
    parser = argparse.ArgumentParser(description='gptctl command line tool')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # init commands
    command_instances = {}
    for command in COMMANDS:
        name = command['name']
        assistant_parser = subparsers.add_parser(name, help=f'{name} commands')
        command_instance = command['instance']
        # command_instance = reflect.generate_instance(clazz, command.get('init_args', {}))
        command_instance.init_parser(assistant_parser)
        command_instances[name] = command_instance

    #  parse args
    args = parser.parse_args()

    # init context
    context = Context()

    # execute subcommand
    command_instance = command_instances.get(args.subcommand)
    if not command_instance:
        exit(f'No subcommand {args.subcommand} found.')
    command_instance.execute(context, args)


if __name__ == '__main__':
    main()
