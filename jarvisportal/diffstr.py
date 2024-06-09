
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

def _new_content(modified_lines, new_lines, start):
    new_content_lines = modified_lines[start-1:start + len(new_lines) + 1]
    new_content = ""
    for i, line in enumerate(new_content_lines):
        new_content += f"{start+i}:{line}"
    return new_content

def applydiff1(original_text: str, start: int, diff: str):
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
    new_content = _new_content(modified_lines, new_lines, start)

    return ''.join(modified_lines), new_content

def _mistakenly_when_adding_empty_line_on_top_of_empty_line(io, id, orig_line, diff_line, original_lines, diff_lines):
    if len(diff_lines) <= id+1 or len(original_lines) <= io+1:
        return False
    next_diff_line = diff_lines[id+1]
    next_orig_line = original_lines[io+1]
    if not next_diff_line.startswith(('+', '-')):
        if not same(orig_line, next_orig_line) and same(next_orig_line, next_diff_line):
            # TODO: explain
            return True
    return False

def _new_line(io, id, orig_line, diff_line, original_lines, diff_lines, log):
    orig_line_noeol = orig_line[:-1] if orig_line else None
    if diff_line.startswith('+'):
        if _mistakenly_when_adding_empty_line_on_top_of_empty_line(io, id, orig_line, diff_line, original_lines, diff_lines):
            new_line = orig_line
            io += 1
            log += f"WARN <diffline {id+1}> mistakenly_when_adding_empty_line_on_top_of_empty_line. [{orig_line_noeol}]~=[{diff_line}]\n"
        else:
            new_line = diff_line[1:] + '\n'
            log += f"OK <diffline {id+1}> added [{diff_line}]\n"
    elif diff_line.startswith('-'):
        if not same(orig_line, diff_line):
            log += f"ERR <diffline {id+1}> mismatch. [{orig_line_noeol}]!=[{diff_line}]\n"
            raise ValueError(log)
        new_line = None
        io += 1
        log += f"OK <diffline {id+1}> removed. [{orig_line_noeol}]==[{diff_line}]\n"
    else:
        if not same(orig_line, diff_line):
            log += f"ERR <diffline {id+1}> mismatch. [{orig_line_noeol}]!=[{diff_line}]\n"
            raise ValueError(log)
        if orig_line is None:
            log += f"ERR <diffline {id+1}> mismatch. [EOF]!=[{diff_line}]\n"
            raise ValueError(log)
        new_line = orig_line
        io += 1
        log += f"OK <diffline {id+1}> kept. [{orig_line_noeol}]==[{diff_line}]\n"
    id += 1
    return io, id, new_line, log

def applydiff(original_text: str, start: int, diff: str):
    validatediff(diff)
    diff = remove_empty_lines_from_start_and_end(diff)
    start -= 1
    original_lines = original_text.splitlines(keepends=True)
    diff_lines = diff.splitlines()

    if start > 1 and len(diff_lines) > 0 and diff_lines[0].startswith(('+', '-')):
        raise ValueError("The first line of the diff cannot be an addition or subtraction when start > 1. Confirm the content you want to change by providing a lower start and the first diff line with a space.")
    
    start, diff = adjust_parameters_with_some_room_for_error(original_text, start, diff)
    diff_lines = diff.splitlines()

    new_lines = []
    io, id = start, 0
    log = "start diff validation...\n"
    while id < len(diff_lines):
        diff_line = diff_lines[id]
        orig_line = original_lines[io] if io < len(original_lines) else None
        io, id, new_line, log = _new_line(io, id, orig_line, diff_line, original_lines, diff_lines, log)
        if new_line is not None:
            new_lines.append(new_line)
    modified_lines = original_lines[:start] + new_lines + original_lines[io:]
    new_content = _new_content(modified_lines, new_lines, start)
    return ''.join(modified_lines), new_content
    
