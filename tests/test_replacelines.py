from jarvisportal.replacelinesstr import replacelines


original_content = '''hello

I am a file
I have content

Being a file
Makes me happy

Goodbye
'''

def test_apply_diff_success():
    lines_find = '''I am a file
I have content

Being a file
Makes me happy
'''
    lines_replace = '''I am a file
I have good content

Being a file
Makes me very happy
'''

    result = replacelines(original_content, lines_find, lines_replace)

    expected_content = '''hello

I am a file
I have good content

Being a file
Makes me very happy

Goodbye
'''
    assert result == expected_content, "Content does not match expected content"

def test_partial_line_match():
    lines_find = '''a file
I have content

Being a file
Makes me happy
'''
    lines_replace = '''a file
I have good content

Being a file
Makes me very happy
'''

    try:
        replacelines(original_content, lines_find, lines_replace)
    except ValueError as e:
        assert str(e) == 'Partial line match not allowed: [a file]'

    else:
        assert False, "Expected ValueError was not raised"
