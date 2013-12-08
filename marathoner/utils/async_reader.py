import threading


class AsyncReader(threading.Thread):
    '''Asynchronously read lines from the stream and call the callback function
    for each line.
    '''
    def __init__(self, stream, cb):
        super(AsyncReader, self).__init__()
        self.stream = stream
        self.cb = cb

    def run(self):
        while True:
            try:
                line = self.stream.readline()
            except:
                break
            if not line:
                break
            self.cb(line)
