import random
import string


def random_number_substitution(code, padded_length=10):
    """
    Randomly substitute digits in a code with other digits, and pad the code with random digits if necessary.
    After 10 digits, there's no need to pad the code since the chances of a collision are very low.
    """
    output = "".join([random.choice(string.digits) if c.isdigit() else c for c in code])
    n_digits = sum(c.isdigit() for c in code)
    if n_digits < padded_length:
        output += "".join(random.choices(string.digits, k=padded_length - n_digits))
    return output
