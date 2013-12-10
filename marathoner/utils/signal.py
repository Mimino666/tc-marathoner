import signal

from six import iteritems


_names = dict((k, v) for v, k in iteritems(signal.__dict__) if v.startswith('SIG'))

def get_signal_name(signal_code):
    name = _names.get(signal_code, '')
    if name:
        return '%s (%s)' % (signal_code, name)
    else:
        return '%s' % signal_code
