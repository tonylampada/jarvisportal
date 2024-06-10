import sys
import os
import json
import subprocess
from .bunch import Bunch
from .diffstr import applydiff
from .replacelinesstr import replacelines

cli_input = sys.stdin
cmd = '\U0001F47B'


def set_cli_input(input_stream):
    global cli_input
    cli_input = input_stream

class ActionCreateFile():
    def prompt(self, path: str, content: str):
        print(f"{cmd} create file {path}")
    
    def run(self, path: str, content: str):
        """this function is used to create a file
        :param path: file path
        :param content: file content. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.
        """
        path = os.path.expanduser(path)
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

class ActionReadFileWithLineNumbers():
    def prompt(self, path: str):
        print(f"{cmd} read file {path} with line numbers")

    def run(self, path: str):
        """
        Reads a file and prefixes each line with its line number.
        :param path: file path
        :return: the content of the file with line numbers
        """
        if not os.path.exists(path):
            print(f"ERROR: file {path} doesn't exist")
            return {"error": f"file {path} doesn't exist. Please provide a valid file path."}

        with open(path, 'r') as file:
            lines = file.readlines()

        numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]
        content_with_line_numbers = "".join(numbered_lines)
        
        return content_with_line_numbers

class ActionUpdateFileLines():
    def prompt(self, path: str, line_start: int, line_end: int, content: str):
        print(f"{cmd} update file {path} from line {line_start} to {line_end}")

    def run(self, path: str, line_start: int, line_end: int, content: str):
        """Edits a file between lines [start-end] (the indices are 0-based and inclusive in both ends). Example, let's say myfile.txt has contents ABCDEF (each letter in a line). Then updateFile(myfile.txt, 2, 4, 'X\nY\nZ\n') would result in ACXYZEF (each letter in a line)
        :param path: file path
        :param line_start: line to start replacing content (0-based, inclusive)
        :param line_env: line to end replacing content (0-based, inclusive)
        :param content: the content to replace. Must end with \n. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.
        """
        if not os.path.exists(path):
            print(f"ERROR: file {path} doesnt exist")
            return {"error": f"file {path} doesnt exist. Use createFile instead"}
        with open(path, "r") as file:
            lines = file.readlines()
        lines[line_start:line_end] = content.splitlines(keepends=True)
        with open(path, "w") as file:
            file.writelines(lines)
        return "".join(lines) # TODO: check if returned value is correct

class ActionUpdateFileAnchors():
    def prompt(self, path: str, start_anchor: str, end_anchor: str, content: str):
        print(f"{cmd} update file {path}")
        print(f"[replace]\n{start_anchor}\n...\n{end_anchor}\n[with]\n{content}[/replace]")

    def run(self, path: str, start_anchor: str, end_anchor: str, content: str):
        """Edits a file based on text anchors. This function replaces text between specified start and end anchors with new content. Anchors are specific words, phrases, or characters identified in the file. In other words, the string '${start_anchor}...${end_anchor}' will be replaced with '${content}'.
        :param path: file path
        :param start_anchor: The anchor text marking the beginning of the text to be replaced. The function will start replacing text starting on this anchor. The anchor itself will also be replaced.
        :param start_anchor: The anchor text marking the end of the text to be replaced. The function will stop replacing text at the end of this anchor. The anchor itself will also be replaced.
        :param content: The new content to replace between the start and end anchors. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.
        """
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
        return updated_data

class ActionUpdateFileReplace():
    def prompt(self, path: str, old_content: str, new_content: str):
        print(f"{cmd} update file {path}")
        print(f"[replace]\n{old_content}\n[with]\n{new_content}[/replace]")

    def run(self, path: str, old_content: str, new_content: str):
        """Replaces all instances of old_content with new_content in a file
        :param path: file path
        :param old_content: the content to replace
        :param new_content: the content to replace with
        """
        with open(path, 'r') as file:
            data = file.read()
        updated_data = data.replace(old_content, new_content)
        with open(path, 'w') as file:
            file.write(updated_data)
        return updated_data

class ActionUpdateFileDiff():
    def prompt(self, path: str, start: str, diff: str):
        print(f"{cmd} apply diff {path} (from line {start})")
        print(diff)

    def run(self, path: str, start: str, diff: str):
        with open(path, 'r') as file:
            content = file.read()
        result, new_content = applydiff(content, start, diff)

        with open(path, 'w') as file:
            file.write(result)
        return new_content

class ActionUpdateFileReplaceLines():
    def prompt(self, path: str, lines_find: str, lines_replace: str):
        print(f"""{cmd} apply diff {path}
----- find
{lines_find}
----- replace with
{lines_replace}""")

    def run(self, path: str, lines_find: str, lines_replace: str):
        with open(path, 'r') as file:
            content = file.read()
        result = replacelines(content, lines_find, lines_replace)

        with open(path, 'w') as file:
            file.write(result)
        return True


class ActionExec():
    def prompt(self, command: str):
        print(f"{cmd} exec {command}")
    
    def run(self, command):
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

ACTIONS = {
    "createFile": ActionCreateFile(),
    "readFileWithLineNumbers": ActionReadFileWithLineNumbers(),
    "updateFile_lines": ActionUpdateFileLines(),
    "updateFile_anchors": ActionUpdateFileAnchors(),
    "updateFile_replace": ActionUpdateFileReplace(),
    "updateFile_diff": ActionUpdateFileDiff(),
    "updateFile_replacelines": ActionUpdateFileReplaceLines(),
    "exec": ActionExec(),
}

def exec_actions(actions, ask=False):
    return [exec_action(action, ask=ask) for action in actions]

def exec_action(action, ask=False):
    if isinstance(action, dict):
        action = Bunch(action)
    if(isinstance(action.function.arguments, str)):
        try:
            action.function.arguments = json.loads(action.function.arguments)
        except Exception as e:
            errmsg = f"Error parsing json from GPT: {e} - arguments={action.function}"
            print(errmsg)
            return {
                # "id": action.get("id"),
                "error": errmsg
            }
    arguments = dict(action.function.arguments)
    try:
        runaction = ACTIONS[action.function.name]
    except Exception as e:
        print(f"Error finding function: {e}")
        return {
            # "id": action.get("id"),
            "error": f"Error finding function: {e}"
        }
    try:
        print("debug")
        print(arguments)
        runaction.prompt(**arguments)
    except Exception as e:
        return {
            # "id": action.get("id"),
            "error": f"Error executing action: {e}"
        }
    if ask:
        answer = input("Run? [Y/n] ").lower()
        if answer == "n":
            return {
                # "id": action.get("id"),
                "error": "denied by user"
            }
    try:
        result = runaction.run(**arguments)
        return result
        # return {
            # "id": action.get("id"),
        #     "output": result
        # }
    except Exception as e:
        print(f"Error running command: {e}")
        return {
            # "id": action.get("id"),
            "error": f"Error running command: {e}"
        }

definitions = [
    {
        "name": "createFile",
        "description": "Creates a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "file path."},
                "content": {
                    "type": "string",
                    "description": "file content. Remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "readFileWithLineNumbers",
        "description": "Reads a file and prefixes each line with its line number. Use this before updateFile_diff.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "updateFile_diff",
        "description": "Updates a file by applying a diff. Returns a snippet of the lines changed, with line numbers. If there's an error, the error message contains a debug log that should help you see what's wront with the diff.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "file path."},
                "start": {"type": "integer", "description": "first line that the diff refers to (1-based)"},
                "diff": {
                    "type": "string",
                    "description": "diff to apply, in simplified unified diff format (without headers). each line is prefixed by + for added lines, - for removed lines, or space for unchanged lines.",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "updateFile_replaceLines",
        "description": "Replaces all instances of old_content with new_content in a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "file path."},
                "lines_find": {"type": "string", "description": "the lines to find"},
                "lines_replace": {"type": "string", "description": "the lines to replace with"}
            },
            "required": ["path", "lines_find", "lines_replace"]
        }
    },
    {
        "name": "exec",
        "description": "Executes a shell command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to be executed"}
            },
            "required": ["command"],
        },
    },
]
