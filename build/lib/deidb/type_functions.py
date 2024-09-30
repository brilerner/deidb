import random
import string


def random_number_substitution(code):
    return "".join([random.choice(string.digits) if c.isdigit() else c for c in code])
