from src.utils.common import *
from src.libopenai.assistant import *

# lambda functions
parse_tools = lambda __tools: [{"type": item} for item in __tools.split(",")] if __tools else None
parse_assistant_info = lambda \
    v: f"{v.id}\n\tname = {v.name}\n\tdescription = {v.description}\n\tinstructions = {v.instructions}\n\tmodel = {v.model}\n\ttools = {v.tools}\n\tfile_ids = {v.file_ids}"


class AssistantCommand:

    def __init__(self):
        pass

    def init_parser(self, parser):
        # action
        parser.add_argument("--create", action="store_true", help="Action: create new assistant")
        parser.add_argument("--update", action="store_true", help="Action: update specified assistant")
        parser.add_argument("--list", action="store_true", help="Action: list assistants")
        parser.add_argument("--delete", action="store_true", help="Action: delete specified assistants")
        parser.add_argument("--choose", action="store_true", help="Action: choose assistant")
        # id
        parser.add_argument("--id", help="assistant id")
        # info group
        list_group = parser.add_argument_group("assistant info")
        list_group.add_argument("--name", help="name")
        list_group.add_argument("--description", help="description")
        list_group.add_argument("--instructions", help="instructions")
        list_group.add_argument("--file_ids", help="file ids")
        list_group.add_argument("--model", help="model")
        list_group.add_argument("--tools", help="tools, separated by comma")

    def execute(self, context, args):
        if args.create:
            check_required_args(args, ["name"])
            logging.info(f"creating assistant: name={args.name}, description={args.description},"
                         f" model={args.model}, tools={args.tools}, file_ids={args.file_ids}")
            xargs = parse_valid_assistant_args(args)
            assistant = create(xargs)
            logging.info(f"created assistant: {parse_assistant_info(assistant)}")
        elif args.list:
            assistants = get_all()
            for i, v in enumerate(assistants):
                print(f"assistant-{i+1}: {parse_assistant_info(v)}")
        elif args.choose:
            # id or name is required
            check_required_args(args, [("id", "name")])
            condition = {"id": args.id} if args.id else {"name": args.name}
            logging.info(f"choosing assistant: condition={condition}")
            assistant = get_by_id_or_name(id=args.id, name=args.name)
            if not assistant:
                exit(f"assistant with condition {condition} not found")
            logging.info(f"chosen assistant: {parse_assistant_info(assistant)}")
            # set assistant id
            context.set_assistant_id(assistant.id)
        elif args.update:
            assistant_id = get_assistant_id(context, args)
            xargs = parse_valid_assistant_args(args)
            xargs["assistant_id"] = assistant_id
            logging.info(f"updating assistant: {xargs}")
            assistant = update(xargs)
            logging.info(f"updated assistant: {parse_assistant_info(assistant)}")
        elif args.delete:
            assistant_id = get_assistant_id(context, args)
            user_input = input(f"Are you sure you wish to delete assistant {assistant_id} ？(yes/no): ").lower()
            if user_input != "yes":
                logging.debug(f"cancelled deleting assistant {assistant_id}")
                exit("cancelled")
            logging.debug(f"deleting assistant: {assistant_id}")
            deleted = delete_if_exists(id=assistant_id)
            if deleted:
                context.set_assistant_id(None)
                logging.info(f"deleted assistant: {deleted}")
            else:
                logging.info(f"assistant {assistant_id} not found")
        else:
            exit(f"action not found, valid actions: create, update, list, delete, choose")


def get_assistant_id(context, args):
    assistant_id = args.id
    if not assistant_id:
        assistant_id = context.get_assistant_id()
    if not assistant_id:
        exit("assistant id not found, please specify with --id or "
             "choose one with --choose --name <name> before this operation.")
    return assistant_id


def parse_valid_assistant_args(args):
    __xargs = {k: v for k, v in vars(args).items()
               if k in ["name", "description", "model", "tools", "instructions", "file_ids"]
               and v is not None}
    if "tools" in __xargs:
        __xargs["tools"] = parse_tools(__xargs["tools"])
    if "file_ids" in __xargs:
        __xargs["file_ids"] = __xargs["file_ids"].split(",")
    return __xargs
