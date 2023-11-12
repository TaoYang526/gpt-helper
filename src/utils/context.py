import os
import logging
from src.utils.common import *
import openai

ENV_KEY_OPENAI_API_KEY = 'OPENAI_API_KEY'
ENV_KEY_LOG_LEVEL = 'LOG_LEVEL'

LOCAL_ENV_FILE = "env.json"
LOCAL_ENV_KEY_ASSISTANT_ID = "ASSISTANT_ID"
LOCAL_ENV_KEY_THREAD_ID = "THREAD_ID"

HOME_DIR = "~/.gpt-helper"


class Context:

    def __init__(self):
        # OpenAI API key is required
        openai.api_key = os.getenv(ENV_KEY_OPENAI_API_KEY)
        if not openai.api_key:
            exit(f"environment var {ENV_KEY_OPENAI_API_KEY} not found!")

        # init logging
        log_level = os.getenv(ENV_KEY_LOG_LEVEL)
        if log_level:
            log_level = logging.getLevelNamesMapping().get(log_level.upper())
            if log_level is None:
                exit(f"invalid log level {log_level}, valid options: {list(logging.getLevelNamesMapping().keys())}")
        log_level = logging.INFO if not log_level else log_level
        logging.basicConfig(stream=None, level=log_level,
                            format='%(asctime)s - %(levelname)s: %(message)s')

        # init home dir
        self.__home_dir = os.path.expanduser(HOME_DIR)
        if not os.path.exists(self.__home_dir):
            os.mkdir(self.__home_dir)
        logging.info(f"initialized context: home_dir={self.__home_dir}, log_level={logging.getLevelName(log_level)}")

        # init env
        self.__env_file = os.path.join(self.__home_dir, LOCAL_ENV_FILE)
        self.__env = None

    def get_env(self):
        if self.__env is not None:
            return self.__env
        return self.__load_env()

    def __load_env(self):
        # load if not exit
        if os.path.exists(self.__env_file):
            self.__env = load_dict(self.__env_file)
            logging.info("loaded env={}".format(self.__env))
        else:
            self.__env = {}
            logging.info("skip loading env since env file {} does not exist!".format(self.__env_file))
        return self.__env

    def add_env_entry(self, key, value):
        env = self.get_env()
        env[key] = value
        self.__persist_env()

    def __persist_env(self):
        save_dict(self.__env_file, self.__env)
        logging.info("persisted env: {}".format(self.__env))

    def get_assistant_id(self):
        return self.get_env().get(LOCAL_ENV_KEY_ASSISTANT_ID)

    def get_thread_id(self):
        return self.get_env().get(LOCAL_ENV_KEY_THREAD_ID)

    def set_assistant_id(self, assistant_id):
        self.add_env_entry(LOCAL_ENV_KEY_ASSISTANT_ID, assistant_id)

    def set_thread_id(self, thread_id):
        self.add_env_entry(LOCAL_ENV_KEY_THREAD_ID, thread_id)

    def get_home_dir(self):
        return self.__home_dir