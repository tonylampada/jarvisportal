import pytest
from gptexec import action_exec

def test_action_exec():
    result = action_exec('echo "Hello, World!"')
    assert result['output'] == 'Hello, World!\n'