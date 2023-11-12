import logging

import openai


def get_all():
    return openai.beta.assistants.list()


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


def update():
    pass