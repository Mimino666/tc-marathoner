import threading


class AsyncReader(threading.Thread):
    '''Asynchronously read lines from the stream and call the callback function
    for each line.
    '''
    def __init__(self, stream, callback):
        super(AsyncReader, self).__init__()
        self.stream = stream
        self.callback = callback

    def run(self):
        while True:
            try:
                line = self.stream.readline()
            except:
                return
            if not line:
                return
            if self.callback(line):
                return
