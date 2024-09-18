def is_kinda_same(a: str, b: str):
    """Helper function to losely compare two strings.

    Args:
        a (str): Any valid string
        b (str): Any valid string

    Returns:
        bool: Return `True` or `False` based on if two strings are (kinda) same.
    """
    if (
        a.lower() != b.lower()
        and a.lower() not in b.lower()
        and b.lower() not in a.lower()
    ):
        return False

    else:
        return True
