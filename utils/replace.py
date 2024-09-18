def replace_after_half(text: str, replace: str = "x") -> str:
    """Replace a given string with "x" or user provided string after half of it's length, except "."

    Args:
        text (str): Any string.
        replace (str, optional): String to replce with. Defaults to "x".

    Returns:
        str: Modified string with characters being replaced with "x" or provided `replace` after the half length of string.
    """
    result = ""

    half_index = len(text) // 2

    for i, char in enumerate(text):
        if i >= half_index and char != ".":
            result += replace

        else:
            result += char

    return result


if __name__ == "__main__":

    ips = ["127.0.0.1", "192.168.69.69"]

    for ip in ips:
        print(replace_after_half(ip))
