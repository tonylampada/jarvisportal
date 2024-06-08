
def validatediff(diff):
    if not diff:
        raise ValueError("Diff is empty")
    diff_lines = diff.splitlines()
    changing_lines = [l for l in diff_lines if l.startswith(('+', '-'))]
    if not changing_lines:
        raise ValueError("This diff is not changing anything. Add lines with +, remove with -")

def remove_empty_lines_from_start_and_end(s):
    lines = s.splitlines()
    if not lines:
        return s
    while lines[0] == '':
        lines = lines[1:]
    while lines[-1] == '':
        lines = lines[:-1]
    return '\n'.join(lines)

def remove_anchors_from_end(s):
    lines = s.splitlines()
    if not lines:
        return s
    while not lines[-1].startswith(('+', '-')):
        lines = lines[:-1]
    return '\n'.join(lines)

def same(lo, ld):
    if len(ld) > 0 and ld[0] == '-':
        ld = ld[1:]
    return lo.strip() == ld.strip()

def adjust_parameters_with_some_room_for_error(original_text, start, diff):
    if start == 0:
        return start, diff
    diff_lines = diff.splitlines()
    if not diff_lines:
        return start, diff
    original_lines = original_text.splitlines(keepends=True)
    if not same(diff_lines[0], original_lines[start]):
        for r in range(1, 3):
            if same(diff_lines[0], original_lines[start + r]):
                return start + r, diff
    return start, diff

def applydiff(original_text: str, start: int, diff: str):
    validatediff(diff)
    diff = remove_empty_lines_from_start_and_end(diff)
    diff = remove_anchors_from_end(diff)
    start -= 1
    original_lines = original_text.splitlines(keepends=True)

    diff_lines = diff.splitlines()

    if start > 1 and len(diff_lines) > 0 and diff_lines[0].startswith(('+', '-')):
        raise ValueError("The first line of the diff cannot be an addition or subtraction when start > 1. Confirm the content you want to change by providing a lower start and the first diff line with a space.")
    
    start, diff = adjust_parameters_with_some_room_for_error(original_text, start, diff)
    diff_lines = diff.splitlines()
    
    line_end_orig = start + len([line for line in diff_lines if not line.startswith('+')])
    original_segment = original_lines[start:line_end_orig]

    new_lines = []
    unchanged_lines = []
    for line in diff_lines:
        if line.startswith('+'):
            new_lines.append(line[1:] + '\n')
        elif line.startswith('-'):
            unchanged_lines.append(line+'\n')
        else:
            new_line = line[1:] if line.startswith(' ') else line
            new_lines.append(new_line + '\n')
            unchanged_lines.append(line + '\n')
    errmsg = "start diff validation...\n"
    for i, (orig_line, unchanged_line) in enumerate(zip(original_segment, unchanged_lines)):
        if not same(orig_line, unchanged_line):
            errmsg += f"> line {i + start + 1} does NOT match. This is an error!\n"
            errmsg += f" {orig_line}"
            errmsg += unchanged_line
            raise ValueError(errmsg)
        else:
            errmsg += f"> line {i + start + 1} matches. OK!\n"
            errmsg += f" {orig_line}"
            errmsg += unchanged_line

    modified_lines = original_lines[:start] + new_lines + original_lines[line_end_orig:]
    new_content_lines = modified_lines[start-1:start + len(new_lines) + 1]
    new_content = ""
    for i, line in enumerate(new_content_lines):
        new_content += f"{start+i}:{line}"

    return ''.join(modified_lines), new_content
