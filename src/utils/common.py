import json
import os
import logging


def check_required_args(args, required_names):
    not_found_keys = []
    for name in required_names:
        if isinstance(name, tuple):
            if not any([getattr(args, n, None) for n in name]):
                not_found_keys.append(" or ".join(name))
        elif not getattr(args, name, None):
            not_found_keys.append(name)
    if not_found_keys:
        exit(f"ERROR: {not_found_keys} is required but not found")


def save_dict(path, target_dict, encoding="utf-8"):
    json.dump(target_dict, open(path, 'w', encoding=encoding))


def load_dict(path, encoding="utf-8"):
    return json.load(open(path, encoding=encoding))


def read_files_content_if_exists(files):
    files_content = ""
    if files:
        files = files.split(",")
        for file in files:
            if not os.path.exists(file):
                logging.warning(f"file {file} not exists, skipped")
                continue
            with open(file, "r") as f:
                files_content += f"content of {f.name}:\n{f.read()}\n"
    return files_content
