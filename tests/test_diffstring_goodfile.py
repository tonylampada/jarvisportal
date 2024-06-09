from jarvisportal.diffstr import applydiff

original_content = '''hello

I am a file
I have content

Being a file
Makes me happy
'''

def test_apply_diff_success():
    diff = ''' I am a file
-I have content
+I have good content
 
 Being a file
-Makes me happy
+Makes me very happy
'''

    result = applydiff(original_content, 3, diff)[0]

    expected_content = '''hello

I am a file
I have good content

Being a file
Makes me very happy
'''
    assert result == expected_content, "Content does not match expected content"

def test_non_matching_lines():
    diff = ''' I am a file
-I do not match
+I have good content
 
 Being a file
-Makes me happy
+Makes me very happy
'''

    try:
        applydiff(original_content, 3, diff)
    except ValueError as e:
        assert str(e) == """start diff validation...
OK <diffline 1> kept. [I am a file]==[ I am a file]
ERR <diffline 2> mismatch. [I have content]!=[-I do not match]
"""
    else:
        assert False, "Expected ValueError was not raised"

import os
from jarvisportal.actions import ActionUpdateFileDiff

def test_empty_diff():
    diff = ''
    try:
        applydiff(original_content, 3, diff)
    except ValueError as e:
        assert str(e) == "Diff is empty"
    else:
        assert False, "Expected ValueError was not raised"

def test_add_lines():
    diff = ''' I am a file
+I have new content
 I have content
 
 Being a file
'''

    result = applydiff(original_content, 3, diff)[0]

    expected_content = '''hello

I am a file
I have new content
I have content

Being a file
Makes me happy
'''
    assert result == expected_content, "Content does not match expected content"

def test_remove_lines():
    diff = ''' I am a file
-I have content
 
 Being a file
'''

    result = applydiff(original_content, 3, diff)[0]

    expected_content = '''hello

I am a file

Being a file
Makes me happy
'''
    assert result == expected_content, "Content does not match expected content"

def test_modify_multiple_lines():
    diff = ''' I am a file
-I have content
+I have updated content
 
 Being a file
-Makes me happy
+Makes me very happy
'''

    result = applydiff(original_content, 3, diff)[0]
    expected_content = '''hello

I am a file
I have updated content

Being a file
Makes me very happy
'''
    assert result == expected_content, "Content does not match expected content"

def test_no_matching_lines():
    diff = ''' I am a file
-I do not match
+I have good content
 Being a file
'''

    try:
        applydiff(original_content, 3, diff)
    except ValueError as e:
        assert str(e) == """start diff validation...
OK <diffline 1> kept. [I am a file]==[ I am a file]
ERR <diffline 2> mismatch. [I have content]!=[-I do not match]
"""
    else:
        assert False, "Expected ValueError was not raised"

def test_invalid_start_with_diff():
    diff = '''+I have new content
 I am a file
 I have content
'''

    try:
        applydiff(original_content, 3, diff)
    except ValueError as e:
        assert str(e) == "The first line of the diff cannot be an addition or subtraction when start > 1. Confirm the content you want to change by providing a lower start and the first diff line with a space."
    else:
        assert False, "Expected ValueError was not raised"
