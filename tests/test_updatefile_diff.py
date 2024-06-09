import os
from jarvisportal.actions import ActionUpdateFileDiff

def test_apply_diff_success():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_update_diff.txt'
    diff = ''' I am a file
-I have content
+I have good content
 
 Being a file
-Makes me happy
+Makes me very happy
'''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    ActionUpdateFileDiff().run(filepath, 3, diff)

    with open(filepath, 'r') as file:
        content = file.read()

    expected_content = '''hello

I am a file
I have good content

Being a file
Makes me very happy
'''
    assert content == expected_content, "Content does not match expected content"
    os.remove(filepath)

def test_non_matching_lines():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_non_matching_diff.txt'
    diff = ''' I am a file
-I do not match
+I have good content
 
 Being a file
-Makes me happy
+Makes me very happy
'''

    # Create the file with original content
    if os.path.exists(filepath):
        os.remove(filepath)

    with open(filepath, 'w') as file:
        file.write(original_content)

    try:
        ActionUpdateFileDiff().run(filepath, 3, diff)
    except ValueError as e:
        assert str(e) == """start diff validation...
OK <diffline 1> kept. [I am a file]==[ I am a file]
ERR <diffline 2> mismatch. [I have content]!=[-I do not match]
"""
    else:
        assert False, "Expected ValueError was not raised"
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

import os
from jarvisportal.actions import ActionUpdateFileDiff

def test_empty_diff():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_empty_diff.txt'
    diff = ''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    try:
        ActionUpdateFileDiff().run(filepath, 3, diff)
    except ValueError as e:
        assert str(e) == "Diff is empty"
    else:
        assert False, "Expected ValueError was not raised"

def test_add_lines():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_add_lines.txt'
    diff = ''' I am a file
+I have new content
 I have content
 
 Being a file
'''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    ActionUpdateFileDiff().run(filepath, 3, diff)

    with open(filepath, 'r') as file:
        content = file.read()

    expected_content = '''hello

I am a file
I have new content
I have content

Being a file
Makes me happy
'''
    assert content == expected_content, "Content does not match expected content"
    os.remove(filepath)

def test_remove_lines():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_remove_lines.txt'
    diff = ''' I am a file
-I have content
 
 Being a file
'''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    ActionUpdateFileDiff().run(filepath, 3, diff)

    with open(filepath, 'r') as file:
        content = file.read()

    expected_content = '''hello

I am a file

Being a file
Makes me happy
'''
    assert content == expected_content, "Content does not match expected content"
    os.remove(filepath)

def test_modify_multiple_lines():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_modify_multiple_lines.txt'
    diff = ''' I am a file
-I have content
+I have updated content
 
 Being a file
-Makes me happy
+Makes me very happy
'''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    ActionUpdateFileDiff().run(filepath, 3, diff)

    with open(filepath, 'r') as file:
        content = file.read()

    expected_content = '''hello

I am a file
I have updated content

Being a file
Makes me very happy
'''
    assert content == expected_content, "Content does not match expected content"
    os.remove(filepath)

def test_no_matching_lines():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_no_matching_lines.txt'
    diff = ''' I am a file
-I do not match
+I have good content
 Being a file
'''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    try:
        ActionUpdateFileDiff().run(filepath, 3, diff)
    except ValueError as e:
        assert str(e) == """start diff validation...
OK <diffline 1> kept. [I am a file]==[ I am a file]
ERR <diffline 2> mismatch. [I have content]!=[-I do not match]
"""
    else:
        assert False, "Expected ValueError was not raised"
    finally:
        os.remove(filepath)

def test_invalid_start_with_diff():
    original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''
    filepath = '/tmp/testfile_invalid_start_diff.txt'
    diff = '''+I have new content
 I am a file
 I have content
'''

    # Create the file with original content
    os.remove(filepath) if os.path.exists(filepath) else None
    with open(filepath, 'w') as file:
        file.write(original_content)

    try:
        ActionUpdateFileDiff().run(filepath, 3, diff)
    except ValueError as e:
        assert str(e) == "The first line of the diff cannot be an addition or subtraction when start > 1. Confirm the content you want to change by providing a lower start and the first diff line with a space."
    else:
        assert False, "Expected ValueError was not raised"
    finally:
        os.remove(filepath)