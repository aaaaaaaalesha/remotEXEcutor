import platform


def process_rdp(hostname, username, port=3389):
    system_name = platform.system()
    if system_name == 'Windows':
        pass
    elif system_name in ('Linux', 'Darwin'):
        pass