def check_reader_connection():
    from smartcard.System import readers
    reader_list = readers()
    return len(reader_list) > 0

def print_hyperlink(link, text):
    return f'\u001b]8;;{link}\u001b\\{text}\u001b]8;;\u001b\\'
url = "localhost:5000"
link_text = "localhost:5000"


