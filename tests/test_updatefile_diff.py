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
        assert str(e) == "diff does not match (line 4)\n I have content\n-I do not match\n"
    else:
        assert False, "Expected ValueError was not raised"
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
