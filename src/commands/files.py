import openai
import logging
from src.utils.common import *
import os

CONF_KEY_PURPOSE = "purpose"
PURPOSE_FINE_TUNE = "fine-tune"
PURPOSE_ASSISTANTS = "assistants"

# lambda functions
parse_file_info = lambda \
    v: f"{v.id}\n\tid = {v.id}\n\tname = {v.filename}\n\tbytes = {v.bytes}\n\tcreated_at = {v.created_at}"


class FileCommand:

    def __init__(self):
        pass

    def init_parser(self, parser):
        # action
        parser.add_argument("--create", action="store_true", help="Action: create new file")
        parser.add_argument("--update", action="store_true", help="Action: update specified file")
        parser.add_argument("--list", action="store_true", help="Action: list files")
        parser.add_argument("--delete", action="store_true", help="Action: delete specified file")
        # id
        parser.add_argument("--id", help="file id")
        # info group
        list_group = parser.add_argument_group("file info")
        list_group.add_argument("--key", help="key")
        list_group.add_argument("--path", help="path")
        list_group.add_argument("--purpose", choices=[PURPOSE_FINE_TUNE, PURPOSE_ASSISTANTS], help="purpose")

    def execute(self, context, args):
        if args.create:
            check_required_args(args, ["key", "path"])
            if not os.path.exists(args.path):
                exit(f"ERROR: path {args.path} not found")
            xargs = parse_valid_file_args(args)
            logging.info(f"creating file: {xargs}")
            file = openai.files.create(**xargs)
            logging.info(f"created file: key={args.key}, {parse_file_info(file)}")
        elif args.list:
            logging.info(f"listing files...")
            files = openai.files.list(purpose=args.purpose)
            for k, v in enumerate(files):
                print(f"file-{k+1}: {parse_file_info(v)}")
        elif args.delete:
            check_required_args(args, ["id"])
            user_input = input(f"Are you sure you wish to delete file {args.id} ？(yes/no): ").lower()
            if user_input != "yes":
                exit("cancelled")
            print(f"deleting file: {args.id}")
            deleted = openai.beta.files.delete(file_id=args.id)
            print(f"deleted file: {deleted}")


def parse_valid_file_args(args):
    __xargs = {k: v for k, v in vars(args).items()
               if k in [CONF_KEY_PURPOSE]
               and v is not None}
    if CONF_KEY_PURPOSE not in __xargs:
        __xargs[CONF_KEY_PURPOSE] = PURPOSE_ASSISTANTS
    if args.path:
        __xargs["file"] = open(args.path, "rb")
    return __xargs
