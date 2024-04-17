import re

def has_only_english_characters(input_string):
    # Regular expression to match only English characters and white spaces
    pattern = re.compile(r'^[a-zA-Z\s]+$')
    
    # Check if the input string matches the pattern
    if pattern.match(input_string):
        return True
    else:
        return False