import re

def find_all(text, substring):
    return [m.start() for m in re.finditer(re.escape(substring), text)]


def exact_line_matches(text, substring, idx):
    sub_lines = substring.splitlines()
    if idx > 0:
        if text[idx-1] != "\n":
            first_line = sub_lines[0]
            return False, first_line
    idx_end = idx + len(substring)
    if idx_end < len(text) and text[idx_end] != "\n":
        if idx_end + 1 < len(text) and text[idx_end + 1] != "\n":
            last_line = sub_lines[-1]
            return False, last_line
    return True, ""


def replacelines(original_text, lines_find, lines_replace):
    """
    Replace the lines in the original text that match the lines_find with the lines_replace.
    Args:
    original_text (str): The original text to be replaced.
    lines_find (list): The multiline string to be replaced. Must match full lines. Partial line matches will be rejected.
    lines_replace (list): The multiline string to replace the lines_find with.
    """
    if lines_find in original_text:
        find_idxs = find_all(original_text, lines_find)
        find_exact_idxs = [i for i in find_idxs if exact_line_matches(original_text, lines_find, i)[0]]
        if len(find_exact_idxs) > 1:
            raise ValueError("Multiple matches found. Use a bigger search string to edit only one place.")
        elif len(find_exact_idxs) == 0:
            reason = exact_line_matches(original_text, lines_find, find_idxs[0])[1]
            raise ValueError(f"Partial line match not allowed: [{reason}]")
        
        result = original_text.replace(lines_find, lines_replace)
        return result
    else:
        raise ValueError("No exact match found for lines_find in original_text.")
