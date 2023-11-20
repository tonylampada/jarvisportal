import sys
import os
import json
import subprocess

cli_input = sys.stdin
cmd = '\U0001F47B'


def set_cli_input(input_stream):
    global cli_input
    cli_input = input_stream


def action_createFile(path: str, content: str):
    """this function is used to create a file
    :param path: file path
    :param content: file content. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.
    """
    print(f"{cmd} create file {path}")
    parentdir = os.path.dirname(path) or "."
    if not os.path.exists(parentdir):
        print(f"ERROR: parent directory {parentdir} does not exist")
        return {"error": f"parent directory {parentdir} does not exist"}
    if os.path.exists(path):
        print(f"ERROR: file {path} already exists")
        return {"error": f"file {path} already exists. Use updateFile instead"}
    with open(path, "w") as file:
        file.write(content)
    return {"success": True}

def action_updateFile_lines(path: str, line_start: int, line_end: int, content: str):
    """Edits a file between lines [start-end] (the indices are 0-based and inclusive in both ends). Example, let's say myfile.txt has contents ABCDEF (each letter in a line). Then updateFile(myfile.txt, 2, 4, 'X\nY\nZ\n') would result in ACXYZEF (each letter in a line)
    :param path: file path
    :param line_start: line to start replacing content (0-based, inclusive)
    :param line_env: line to end replacing content (0-based, inclusive)
    :param content: the content to replace. Must end with \n. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.
    """
    print(f"{cmd} update file {path} from line {line_start} to {line_end}")
    if not os.path.exists(path):
        print(f"ERROR: file {path} doesnt exist")
        return {"error": f"file {path} doesnt exist. Use createFile instead"}
    with open(path, "r") as file:
        lines = file.readlines()
    lines[line_start:line_end] = content.splitlines(keepends=True)
    with open(path, "w") as file:
        file.writelines(lines)

def action_updateFile_anchors(path: str, start_anchor: str, end_anchor: str, content: str):
    """Edits a file based on text anchors. This function replaces text between specified start and end anchors with new content. Anchors are specific words, phrases, or characters identified in the file. In other words, the string '${start_anchor}...${end_anchor}' will be replaced with '${content}'.
    :param path: file path
    :param start_anchor: The anchor text marking the beginning of the text to be replaced. The function will start replacing text starting on this anchor. The anchor itself will also be replaced.
    :param start_anchor: The anchor text marking the end of the text to be replaced. The function will stop replacing text at the end of this anchor. The anchor itself will also be replaced.
    :param content: The new content to replace between the start and end anchors. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.
    """
    print(f"{cmd} update file {path}")
    print(f"[replace]\n{start_anchor}\n...\n{end_anchor}\n[with]\n{content}[/replace]")
    with open(path, 'r') as file:
        data = file.read()
    start_index = data.find(start_anchor)
    if start_index == -1:
        raise ValueError("Start anchor not found in file.")
    end_index = data.find(end_anchor, start_index)
    if end_index == -1:
        raise ValueError("End anchor not found in file.")
    end_index += len(end_anchor)
    updated_data = data[:start_index] + content + data[end_index:]
    with open(path, 'w') as file:
        file.write(updated_data)

def action_exec(command):
    print(f"{cmd} exec {command}")
    exit_status, output = _cmdexec(command)
    print(f"command status {exit_status}")
    return {"exit": exit_status, "output": output}

def _cmdexec(cmd):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=os.environ,
        stdin=cli_input,  # Allows for user input
        bufsize=0,  # Unbuffered output
        universal_newlines=True
    )
    output = []
    try:
        while True:
            char = process.stdout.read(1)
            if not char:
                break
            sys.stdout.write(char)
            sys.stdout.flush()
            output.append(char)
    except Exception as e:
        sys.stderr.write(f"Error while reading output: {e}\n")
    finally:
        process.stdout.close()
    exit_status = process.wait()
    return exit_status, ''.join(output)

action_runners = {
    "createFile": action_createFile,
    # "updateFile": action_updateFile,
    "exec": action_exec,
}

def exec_actions(actions):
    return [_exec_action(action) for action in actions]

def _exec_action(action):
    try:
        arguments = json.loads(action["function"]["arguments"])
    except Exception as e:
        errmsg = f"Error parsing json from GPT: {e} - arguments={action['function']}"
        print(errmsg)
        return {
            "id": action["id"],
            "output": errmsg
        }
    try:
        function = action_runners[action["function"]["name"]]
    except Exception as e:
        print(f"Error finding function: {e}")
        return {
            "id": action["id"],
            "output": f"Error finding function: {e}"
        }
    
    try:
        return {
            "id": action["id"],
            "output": function(**arguments)
        }
    except Exception as e:
        print(f"Error running command: {e}")
        return {
            "id": action["id"],
            "output": f"Error running command: {e}"
        }
