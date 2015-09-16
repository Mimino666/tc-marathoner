from six.moves import xrange


class Communicator(object):
    def communicate(self, visualizer, solution, visualizer_cb, solution_cb):
        line = visualizer.readline()  # M
        visualizer_cb(line, flush=False)
        M = int(line)
        for i in xrange(M):
            visualizer_cb(visualizer.readline(), flush=False)  # pegValue[i]

        line = visualizer.readline()  # N
        visualizer_cb(line, flush=False)
        N = int(line)
        for i in xrange(N):
            visualizer_cb(visualizer.readline(), flush=False)  # board[i]
        visualizer_cb('', flush=True)

        # read solution
        line = solution.readline()  # ret_length
        solution_cb(line, flush=False)
        ret_length = int(line)
        for i in xrange(ret_length):
            solution_cb(solution.readline(), flush=False)
