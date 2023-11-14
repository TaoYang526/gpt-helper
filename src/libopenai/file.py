import openai


def create(xargs):
    return openai.files.create(**xargs)


def delete(file_id):
    return openai.files.delete(file_id=file_id)


def get_all(purpose):
    return openai.files.list(purpose=purpose)
