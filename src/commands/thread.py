import logging
import os.path

import openai
import time

from src.commands.assistant import get_assistant_id
from src.utils.common import *
from retry import retry
from tinydb import TinyDB, Query

THREADS_DATA_FILE = "threads.json"


class ThreadCommand:

    def __init__(self):
        self.__db = None

    def __get_db(self, context):
        if self.__db:
            return self.__db
        __data_file = os.path.join(context.get_home_dir(), THREADS_DATA_FILE)
        self.__db = TinyDB(__data_file)
        return self.__db

    def init_parser(self, parser):
        # action
        parser.add_argument("--create", action="store_true", help="Action: create new thread")
        parser.add_argument("--update", action="store_true", help="Action: update specified thread")
        parser.add_argument("--list", action="store_true", help="Action: list all threads")
        parser.add_argument("--get", action="store_true", help="Action: get specified thread and list messages")
        parser.add_argument("--choose", action="store_true", help="Action: choose specified thread")
        parser.add_argument("--delete", action="store_true", help="Action: delete specified thread")
        parser.add_argument("--chat", action="store_true", help="Action: chat via specified thread")

        parser.add_argument("--id", help="thread id")
        parser.add_argument("--assistant_id", help="assistant id")
        parser.add_argument("--metadata", help="metadata")
        # info group
        list_group = parser.add_argument_group("thread info")
        list_group.add_argument("--name", help="specified by user and stored locally, used to locate thread")
        list_group.add_argument("--description", help="description")

    def execute(self, context, args):
        if args.create:
            check_required_args(args, ["name"])
            metadata = json.loads(args.metadata) if args.metadata else {}
            metadata["name"] = args.name
            thread = openai.beta.threads.create(messages=[], metadata=args.metadata)
            logging.info(f"created thread: {thread}")
            metadata["id"] = thread.id
            db = self.__get_db(context)
            db.insert(metadata)
            logging.info(f"persisted thread in local DB, thread={metadata}")
        elif args.list:
            db = self.__get_db(context)
            threads = db.all()
            for i, v in enumerate(threads):
                print(f"thread-{i+1}: {v}")
        elif args.choose:
            check_required_args(args, [("id", "name")])
            condition = {"id": args.id} if args.id else {"name": args.name}
            logging.info(f"choosing thread: condition={condition}")
            db = self.__get_db(context)
            cond = None
            for key, value in condition.items():
                if cond is None:
                    cond = getattr(Query(), key) == value
                else:
                    cond &= getattr(Query(), key) == value
            result = db.search(cond)
            if len(result) == 0:
                logging.fatal(f"thread with condition {condition} not found")
            if len(result) > 1:
                logging.fatal(f"multiple threads found with condition {condition}: {result}")
            thread = result[0]
            context.set_thread_id(thread.get('id'))
            logging.info(f"chosen thread: {thread}")
        elif args.update:
            check_required_args(args, ["metadata"])
            metadata = json.loads(args.metadata)
            thread_id = get_thread_id(context, args)
            thread = openai.beta.threads.update(thread_id=thread_id, metadata=metadata)
            logging.info(f"updated thread: {thread}")
        elif args.get:
            thread_id = get_thread_id(context, args)
            msgs = openai.beta.threads.messages.list(thread_id=thread_id)
            logging.info(f"got {len(msgs.data)} messages")
            for msg in msgs:
                print(f"{msg}")
        elif args.chat:
            assistant_id = get_assistant_id(context, args)
            thread_id = get_thread_id(context, args)
            logging.info(f"chatting via thread: {thread_id}")
            while True:
                prompt = input("You: ")
                if prompt.strip() == '':
                    continue
                try:
                    chat(assistant_id, thread_id, prompt)
                except Exception as err:
                    logging.error(f"failed to chat: {err}, please check your network then try again later...")


def get_thread_id(context, args):
    if args.id:
        return args.id
    thread_id = context.get_thread_id()
    if thread_id:
        return thread_id
    exit(f"thread id not found, please specify it via --thread_id or "
         f"choose thread via --choose --name <name> before this operation.")


def parse_message_contents(msg):
    return [f"{v.text.value}" if v.type == 'text' else f"{v}" for v in msg.content]


@retry(tries=5, delay=1, backoff=2)
def chat(assistant_id, thread_id, prompt):
    msg = openai.beta.threads.messages.create(thread_id=thread_id, content=prompt, role='user', timeout=2)
    run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    while run.status not in ["cancelled", "failed", "completed", "expired"]:
        logging.debug(f"run: status={run.status}, waiting for AI to complete...")
        time.sleep(0.5)
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        # msgs = openai.beta.threads.messages.list(thread_id=thread_id, before=msg.id)
        # print(f"latest msgs={msgs}")
    # print(f"AI completed, run status: {run}")
    if run.status == "completed":
        msgs = openai.beta.threads.messages.list(thread_id=thread_id, before=msg.id)
        print(f"AI: (responded {len(msgs.data)} messages)" if len(msgs.data) > 1 else "AI:")
        for msg in msgs:
            contents = parse_message_contents(msg)
            print("[END of content]\n".join(contents))
    else:
        logging.warn(f"AI ran but got non-completed status, run={run}")
