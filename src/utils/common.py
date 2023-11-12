import json


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
