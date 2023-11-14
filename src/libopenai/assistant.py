import logging

import openai


def get_all():
    result = []
    start_index = ''
    while True:
        logging.debug(f"listing assistants with start_index={start_index}")
        assistants = openai.beta.assistants.list(after=start_index)
        for v in assistants:
            result.append(v)
        if not assistants.has_more:
            break
        else:
            start_index = assistants.last_id
    return result


def get_by_name(name):
    assistants = get_all()
    return next((v for v in assistants if v.name == name), None)


def get(id):
    try:
        return openai.beta.assistants.retrieve(assistant_id=id)
    except openai.NotFoundError:
        logging.debug(f"assistant with id {id} not found")
    return None


def get_by_id_or_name(id=None, name=None):
    assistant = None
    if id:
        assistant = get(id=id)
    elif name:
        assistant = get_by_name(name=name)
    return assistant


def delete_if_exists(id):
    try:
        deleted = openai.beta.assistants.delete(assistant_id=id)
        return deleted
    except openai.NotFoundError:
        logging.debug(f"assistant {id} not found")
    return None


def create(xargs):
    return openai.beta.assistants.create(**xargs)


def update(xargs):
    return openai.beta.assistants.update(**xargs)
