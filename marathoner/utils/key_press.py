'''This module implements non-blocking methods waiting for specific key to
be pressed. This thing is hard to do in Python without external libraries,
so forgive me for any non-working hacks below.
'''

def _windows_key_press(wanted_key, kill_event, received_cb):
    '''Check for key presses from stdin in non-blocking way. Check until either
    `wanted_key` was pressed or `kill_event` has been set.
    If we detect `wanted_key` before `kill_event` is set, call `received_cb`
    callback and return.

    @param wanted_key: key to be pressed (in our case "q")
    @type wanted_key: one-letter str

    @param kill_event: indicate to stop reading and return
    @type kill_event: threading.Event

    @param received_cb: called when `wanted_key` was read
    @type received_cb: empty-argument callable
    '''
    import msvcrt
    import time

    wanted_key = wanted_key.lower()
    while not kill_event.is_set():
        if msvcrt.kbhit():
            c = msvcrt.getch()
            if c.lower() == wanted_key:
                received_cb()
                break
        else:
            time.sleep(0.5)


def _linux_key_press(wanted_key, kill_event, received_cb):
    import select
    import sys
    import termios
    import time
    import tty

    def is_data():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    wanted_key = wanted_key.lower()
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while not kill_event.is_set():
            if is_data():
                c = sys.stdin.read(1).lower()
                if c == wanted_key:
                    received_cb()
                    break
            else:
                time.sleep(0.5)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


try:
    import msvcrt
    get_key_press = _windows_key_press
except ImportError:
    get_key_press = _linux_key_press


def test_keypress():
    '''Above code is very platform specific and hackish. We'd better test it.
    '''
    import threading
    kill_event = threading.Event()

    was_received = [False]
    def received():
        was_received[0] = True

    print 'You have 5 seconds to press "q". Go for it...'
    thread = threading.Thread(target=get_key_press, args=['q', kill_event, received])
    thread.start()
    thread.join(5.0)
    kill_event.set()

    if was_received[0]:
        print 'You have managed to press "q". Congratulations!'
    else:
        print 'You didn\'t press "q". What is wrong with you?!'

    # test that stdin is working as expected
    name = raw_input('What is your name? ')
    print 'Your name is:', name


if __name__ == '__main__':
    test_keypress()
