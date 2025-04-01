import re


def is_valid_string(string: str) -> bool:
    """Validate if a string is non-empty, alphanumeric, or contains non-whitespace characters."""
    return bool(string and (string.isalnum() or not string.isspace()))


def mask_string(
    text: str,
    mask: str = "x",
    mask_special_char: bool = False,
    mask_from_start: bool = False,
    mask_from_char: str = None,
    mask_till_char: str = None,
    exclude_bounds: bool = False,
) -> str:
    """Mask a given string with a specified character either from the start, after half of its length,
    from a specific character, or till a specific character.

    Args:
        text (str): The input string to be masked.
        mask (str, optional): The character to mask with. Defaults to "x".
        mask_special_char (bool, optional): Whether to mask special characters like `.`, `;`, etc. Defaults to False.
        mask_from_start (bool, optional): Whether to mask from the start of the string. Defaults to False.
        mask_from_char (str, optional): Start masking from this character (inclusive). Defaults to None.
        mask_till_char (str, optional): Mask till this character (inclusive). Defaults to None.
        exclude_bounds (bool, optional): Whether to exclude `mask_from_char` and `mask_till_char` from masking. Defaults to False.

    Returns:
        str: The masked string with characters replaced by `mask`.
    """
    if not text:
        return ""

    if not isinstance(mask, str) or len(mask) != 1:
        raise ValueError("Mask must be a single character string.")

    if mask_from_char or mask_till_char:
        return _mask_with_char_bounds(
            text,
            mask,
            mask_special_char,
            mask_from_char,
            mask_till_char,
            exclude_bounds,
        )

    text_length = len(text)
    half_index = text_length // 2

    return _mask_with_original_length(
        text, mask, mask_special_char, half_index, mask_from_start
    )


def _mask_with_original_length(
    text, mask, mask_special_char, half_index, mask_from_start
):
    result = []
    mask_length = half_index  # Always mask half the length of the string
    for i, char in enumerate(text):
        if (
            mask_from_start
            and i < mask_length
            and (mask_special_char or char.isalnum())
        ) or (
            not mask_from_start
            and i >= len(text) - mask_length
            and (mask_special_char or char.isalnum())
        ):
            result.append(mask)
        else:
            result.append(char)
    return "".join(result)


def _mask_with_char_bounds(
    text, mask, mask_special_char, mask_from_char, mask_till_char, exclude_bounds
):
    result = list(text)
    start_index = 0
    end_index = len(text)

    if mask_from_char:
        start_match = re.search(re.escape(mask_from_char), text)
        if start_match:
            start_index = start_match.start()
            if exclude_bounds:
                start_index += len(mask_from_char)

    if mask_till_char:
        end_match = re.search(re.escape(mask_till_char), text)
        if end_match:
            end_index = end_match.end()
            if exclude_bounds:
                end_index -= len(mask_till_char)

    for i in range(start_index, end_index):
        if mask_special_char or text[i].isalnum():
            result[i] = mask

    return "".join(result)


if __name__ == "__main__":

    ips = ["127.0.0.1", "192.168.69.69"]

    for ip in ips:
        print(mask_string(ip))

    print(
        mask_string(
            "potato@example.com",
            mask="*",
            mask_special_char=True,
            mask_from_char="@",
            exclude_bounds=True,
        )
    )

    print(
        mask_string(
            "potato@example.com",
            mask="*",
            mask_special_char=True,
            mask_from_start=True,
            mask_till_char="@",
            exclude_bounds=True,
        )
    )
