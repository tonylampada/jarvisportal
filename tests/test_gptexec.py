import pytest
import os
from gptexec import action_exec, action_updateFile

def test_action_exec():
    result = action_exec('echo "Hello, World!"')
    assert result['output'] == 'Hello, World!\n'

def test_double_echo():
    result = action_exec('echo hello && echo goodbye')
    assert result['output'] == 'hello\ngoodbye\n'

def test_action_updateFile():
    test_content = 'Test content'
    test_path = 'testfile.txt'
    # Write test content to a file
    action_updateFile(test_path, test_content)
    # Read content to verify
    with open(test_path, 'r') as file:
        content = file.read()
    # Clean up test file
    os.remove(test_path)
    # Assert test content is written correctly
    assert content == test_content
