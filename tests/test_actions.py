import pytest
import os
import sys
import subprocess
# from jarvisportal.actions import action_exec, action_createFile, action_updateFile_anchors, action_updateFile_lines, action_updateFile_replace, action_updateFile_diff, set_cli_input
from jarvisportal.actions import set_cli_input, ActionExec, ActionCreateFile, ActionUpdateFileAnchors, ActionUpdateFileLines, ActionUpdateFileReplace, ActionReadFileWithLineNumbers
#, ActionUpdateFileDiff

@pytest.fixture(scope='module', autouse=True)
def cli_input_override():
    original_stdin = sys.stdin
    set_cli_input(subprocess.PIPE)
    yield
    set_cli_input(original_stdin)


def test_action_exec():
    result = ActionExec().run('echo "Hello, World!"')
    assert 'Hello, World!' in result['output']

def test_double_echo():
    result = ActionExec().run('echo hello && echo goodbye')
    assert 'hello\n' in result['output']
    assert 'goodbye\n' in result['output']

def test_action_createFile():
    test_content = 'Test content'
    test_path = '/tmp/testfile.txt'
    ActionCreateFile().run(test_path, test_content)
    with open(test_path, 'r') as file:
        content = file.read()
    assert content == test_content
    os.remove(test_path)

def test_action_updateFile_lines():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_update.txt'
    os.remove(filepath) if os.path.exists(filepath) else None
    ActionCreateFile().run(filepath, original_content)
    ActionUpdateFileLines().run(filepath, 2, 4, 'I am a good file\nI have good content\n')
    with open(filepath, 'r') as file:
        content = file.read()
    expected_content = '''hello

I am a good file
I have good content

Being a file
Makes me happy
'''
    assert content == expected_content
    os.remove(filepath)

def test_action_updateFile_anchors():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_update.txt'
    start_anchor = 'I am a f'
    end_anchor = 'ave content'
    new_content = 'I am a good file\nI have good content'

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    # Update the file using anchors
    ActionUpdateFileAnchors().run(filepath, start_anchor, end_anchor, new_content)

    # Read the updated content
    with open(filepath, 'r') as file:
        content = file.read()

    expected_content = '''hello

I am a good file
I have good content

Being a file
Makes me happy
'''
    assert content == expected_content, "Content does not match expected content"
    os.remove(filepath)

def test_action_updateFile_replace():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_update.txt'
    findtext = 'I am a file\nI have content'
    replacetext = 'I am a good file\nI have good content'

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    ActionUpdateFileReplace().run(filepath, findtext, replacetext)

    with open(filepath, 'r') as file:
        content = file.read()

    expected_content = '''hello

I am a good file
I have good content

Being a file
Makes me happy
'''
    assert content == expected_content, "Content does not match expected content"
    os.remove(filepath)

def test_read_file_with_line_numbers():
    original_content = '''hello

I am a file
I have content
Being a file
Makes me happy
'''
    expected_output = '''1: hello
2: 
3: I am a file
4: I have content
5: Being a file
6: Makes me happy
'''

    filepath = '/tmp/testfile_read_with_line_numbers.txt'

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    action = ActionReadFileWithLineNumbers()
    result = action.run(filepath)

    assert result == expected_output, "The content with line numbers does not match the expected output"
    os.remove(filepath)