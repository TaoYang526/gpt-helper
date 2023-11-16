import openai
from retry import retry
import logging
import time


def create(metadata=None):
    return openai.beta.threads.create(messages=[], metadata=metadata)


def delete(thread_id):
    return openai.beta.threads.delete(thread_id=thread_id)


def update(thread_id, metadata=None):
    return openai.beta.threads.update(thread_id=thread_id, metadata=metadata)


# TODO support for pagination.
def get_messages(thread_id):
    return openai.beta.threads.messages.list(thread_id=thread_id)


def parse_message_contents(msg):
    return [f"{v.text.value}" if v.type == 'text' else f"{v}" for v in msg.content]


@retry(tries=3, delay=1, backoff=2)
def chat(assistant_id, thread_id, prompt):
    logging.debug(f"chatting via thread: {thread_id}, prompt={prompt}")
    msg = openai.beta.threads.messages.create(thread_id=thread_id, content=prompt, role='user', timeout=2)
    run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    while run.status not in ["cancelled", "failed", "completed", "expired"]:
        logging.debug(f"run: status={run.status}, waiting for ChatGPT to complete...")
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        # msgs = openai.beta.threads.messages.list(thread_id=thread_id, before=msg.id)
        # logging.info(f"latest msgs={msgs}")
    # print(f"AI completed, run status: {run}")
    if run.status == "completed":
        msgs = openai.beta.threads.messages.list(thread_id=thread_id, before=msg.id)
        print(f"ChatGPT: (responded {len(msgs.data)} messages)" if len(msgs.data) > 1 else "ChatGPT:")
        for msg in msgs:
            contents = parse_message_contents(msg)
            print("[END of content]\n".join(contents))
    else:
        logging.warning(f"ChatGPT ran but got non-completed status, run={run}")
