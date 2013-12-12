import signal


signal_names = {}
for signame in dir(signal):
    if signame.startswith('SIG'):
        signum = getattr(signal, signame)
        if isinstance(signum, int):
            signal_names[signum] = signame


def get_signal_name(signal_code):
    name = signal_names.get(signal_code, '')
    if name:
        return '%s (%s)' % (signal_code, name)
    else:
        return '%s' % signal_code


def install_shutdown_handlers(func):
    '''Install the given function as a signal handler for all common shutdown
    signals (such as SIGINT, SIGTERM, etc).
    '''
    signal.signal(signal.SIGTERM, func)
    signal.signal(signal.SIGINT, func)
    # Catch Ctrl-Break in windows
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, func)
