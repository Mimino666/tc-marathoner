from six.moves import xrange


class Communicator(object):
    def communicate(self, visualizer, solution, visualizer_cb, solution_cb):
        line = visualizer.readline()  # H
        visualizer_cb(line, flush=False)
        for i in xrange(int(line)):
            visualizer_cb(visualizer.readline(), flush=False)  # slide[i]
        visualizer_cb(visualizer.readline(), flush=False)  # medStrength
        visualizer_cb(visualizer.readline(), flush=False)  # killTime
        visualizer_cb(visualizer.readline(), flush=True)  # spreadProb

        # communicate solution <-> visualizer
        while True:
            cmd_line = solution.readline()  # command
            solution_cb(cmd_line, flush=False)
            cmd = cmd_line.strip()
            if cmd == 'ADDMED':
                solution_cb(solution.readline(), flush=True)  # x y
                visualizer_cb(visualizer.readline(), flush=True)  # result
            elif cmd == 'OBSERVE':
                solution_cb('', flush=True)
                h_line = visualizer.readline()  # H
                visualizer_cb(h_line, flush=False)
                for i in xrange(int(h_line)):
                    visualizer_cb(visualizer.readline(), flush=False)
                visualizer_cb('', flush=True)
            elif cmd == 'WAITTIME':
                solution_cb(solution.readline(), flush=True)  # waitTime
                visualizer_cb(visualizer.readline(), flush=True)  # result
            elif cmd == 'END':
                break
            else:
                raise Exception('Invalid command: %s' % cmd)
