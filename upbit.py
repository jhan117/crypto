from ast import literal_eval
import logging


# --------------------------
# - Name : get_env_var
# - Desc : Read token and keys
# - Input
#     Key : key of env.txt
# - Output
#     Value : value of key
# --------------------------
def get_env_var(key):
    try:
        path = './env/env.txt'

        f = open(path, 'r')
        line = f.readline()
        f.close()

        env_dict = literal_eval(line)
        logging.debug(env_dict)

        return env_dict[key]

    except Exception:
        raise
