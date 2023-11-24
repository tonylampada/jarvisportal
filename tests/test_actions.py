import pytest
import os
import sys
import subprocess
from actions import action_exec, action_createFile, action_updateFile_anchors, action_updateFile_lines, action_updateFile_replace, set_cli_input

@pytest.fixture(scope='module', autouse=True)
def cli_input_override():
    original_stdin = sys.stdin
    set_cli_input(subprocess.PIPE)
    yield
    set_cli_input(original_stdin)


def test_action_exec():
    result = action_exec('echo "Hello, World!"')
    assert 'Hello, World!' in result['output']

def test_double_echo():
    result = action_exec('echo hello && echo goodbye')
    assert 'hello\n' in result['output']
    assert 'goodbye\n' in result['output']

def test_action_createFile():
    test_content = 'Test content'
    test_path = '/tmp/testfile.txt'
    action_createFile(test_path, test_content)
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
    action_createFile(filepath, original_content)
    action_updateFile_lines(filepath, 2, 4, 'I am a good file\nI have good content\n')
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
    action_updateFile_anchors(filepath, start_anchor, end_anchor, new_content)

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

    action_updateFile_replace(filepath, findtext, replacetext)

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
    