import logging
import os.path
from src.libopenai.thread import create, delete, update, get_messages, chat
from src.utils.common import *
from tinydb import TinyDB, Query
# readline should be imported to make input content to be editable.
import readline

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
        parser.add_argument("--chat", action="store_true", help="Action: chat via specified assistant and thread")

        parser.add_argument("--id", help="thread id")
        parser.add_argument("--assistant_id", help="assistant id")
        parser.add_argument("--metadata", help="metadata")
        # info group
        list_group = parser.add_argument_group("thread info")
        list_group.add_argument("--name", help="specified by user and stored locally, used to locate thread")
        list_group.add_argument("--description", help="description")
        # chat group
        chat_group = parser.add_argument_group("chat info")
        chat_group.add_argument("--files", help="Action: content of readable files will be sent before chatting.")

    def execute(self, context, args):
        if args.create:
            check_required_args(args, ["name"])
            metadata = json.loads(args.metadata) if args.metadata else {}
            metadata["name"] = args.name
            thread = create(metadata=metadata)
            logging.info(f"created thread: {thread}")
            metadata["id"] = thread.id
            db = self.__get_db(context)
            db.insert(metadata)
            db.close()
            logging.info(f"persisted thread in local DB, thread={metadata}")
        elif args.delete:
            check_required_args(args, [("id", "name")])
            thread = self.get_thread_by_id_or_name(context, id=args.id, name=args.name)
            if not thread:
                exit(f"ERROR: thread {args.id} not found")
            thread_id = thread.get('id')
            deleted_thread = delete(thread_id=thread_id)
            if deleted_thread:
                logging.info(f"deleted thread: {thread}")
            else:
                logging.warning(f"thread {thread_id} has already been deleted")
            db = self.__get_db(context)
            db_to_delete = db.get(Query().id == thread_id)
            if db_to_delete:
                db.remove(doc_ids=[db_to_delete.doc_id])
                logging.info(f"removed thread {thread_id} in local DB")
            else:
                logging.warning(f"thread {thread_id} has already been removed in local DB")
        elif args.list:
            db = self.__get_db(context)
            threads = db.all()
            for i, v in enumerate(threads):
                print(f"thread-{i+1}: {v}")
        elif args.choose:
            check_required_args(args, [("id", "name")])
            thread = self.get_thread_by_id_or_name(context, id=args.id, name=args.name)
            if thread:
                logging.info(f"chosen thread: {thread}")
                context.set_thread_id(thread.get('id'))
            else:
                exit(f"ERROR: thread {args.id} not found")
        elif args.update:
            check_required_args(args, ["metadata"])
            metadata = json.loads(args.metadata)
            thread_id = get_thread_id(context, args)
            thread = update(thread_id=thread_id, metadata=metadata)
            logging.info(f"updated thread: {thread}")
        elif args.get:
            thread_id = get_thread_id(context, args)
            msgs = get_messages(thread_id=thread_id)
            logging.info(f"got {len(msgs.data)} messages")
            for msg in msgs:
                print(f"{msg}")
        elif args.chat:
            assistant_id = get_assistant_id(context, args)
            thread_id = get_thread_id(context, args)
            logging.info(f"chatting via thread={thread_id} and assistant={assistant_id}")
            files_content = read_files_content_if_exists(args.files)
            while True:
                prompt = input("You: ")
                if prompt.strip() == '':
                    continue
                if files_content:
                    prompt = f"{files_content}\n\n{prompt}"
                    files_content = ""
                try:
                    chat(assistant_id, thread_id, prompt)
                except Exception as err:
                    logging.error(f"failed to chat: [{type(err)}] {err}, please check your network then try again later...")

    def get_thread_by_id_or_name(self, context, id=None, name=None):
        condition = {"id": id} if id else {"name": name}
        logging.debug(f"finding thread: condition={condition}")
        db = self.__get_db(context)
        cond = None
        for key, value in condition.items():
            if cond is None:
                cond = getattr(Query(), key) == value
            else:
                cond &= getattr(Query(), key) == value
        result = db.search(cond)
        if len(result) == 0:
            exit(f"ERROR: thread with condition {condition} not found")
        if len(result) > 1:
            exit(f"ERROR: multiple threads found with condition {condition}: {result}")
        return result[0]


def get_assistant_id(context, args):
    assistant_id = args.assistant_id
    if not assistant_id:
        assistant_id = context.get_assistant_id()
    if not assistant_id:
        exit("assistant id not found, please specify with --id or "
             "choose one with --choose --name <name> before this operation.")
    return assistant_id


def get_thread_id(context, args):
    if args.id:
        return args.id
    thread_id = context.get_thread_id()
    if thread_id:
        return thread_id
    exit(f"thread id not found, please specify it via --thread_id or "
         f"choose thread via --choose --name <name> before this operation.")
