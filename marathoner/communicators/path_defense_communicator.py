from six.moves import xrange


class Communicator(object):
    def communicate(self, visualizer, solution, visualizer_cb, solution_cb):
        line = visualizer.readline()  # N
        visualizer_cb(line, flush=False)
        N = int(line)
        visualizer_cb(visualizer.readline(), flush=False)  # money
        for i in xrange(N):
            visualizer_cb(visualizer.readline(), flush=False)  # board[i]
        visualizer_cb(visualizer.readline(), flush=False)  # creepHealth
        visualizer_cb(visualizer.readline(), flush=False)  # creepMoney
        line = visualizer.readline()  # NT
        visualizer_cb(line, flush=False)
        NT = int(line)
        for i in xrange(NT):
            visualizer_cb(visualizer.readline(), flush=False)  # towerType[i]
        visualizer_cb('', flush=True)

        for step in xrange(2000):
            visualizer_cb(visualizer.readline(), flush=False)  # money
            line = visualizer.readline()  # NC
            visualizer_cb(line, flush=False)
            NC = int(line)
            for i in xrange(NC):
                visualizer_cb(visualizer.readline(), flush=False)  # creep[i]
            line = visualizer.readline()  # B
            visualizer_cb(line, flush=False)
            B = int(line)
            for i in xrange(B):
                visualizer_cb(visualizer.readline(), flush=False)  # baseHealth[i]
            visualizer_cb('', flush=True)

            # read solution
            line = solution.readline() # ret
            solution_cb(line, flush=False)
            M = int(line)
            for i in xrange(M):
                solution_cb(solution.readline(), flush=False)
            # don't flush the last line, because visualizer will immediately quit
            if step+1 < 2000:
                solution_cb('', flush=True)
