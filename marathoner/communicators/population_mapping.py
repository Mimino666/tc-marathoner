from six.moves import xrange


class Communicator(object):
    def communicate(self, visualizer, solution, visualizer_cb, solution_cb):
        visualizer_cb(visualizer.readline(), flush=False)  # maxPercentage
        line = visualizer.readline()  # H
        visualizer_cb(line, flush=False)
        for i in xrange(int(line)):
            visualizer_cb(visualizer.readline(), flush=False)  # worldMap[i]
        visualizer_cb(visualizer.readline(), flush=True)  # totalPopulation

        # communicate solution <-> visualizer
        while True:
            line = solution.readline()
            if line.strip() != '?':
                break
            solution_cb(line, flush=False)
            solution_cb(solution.readline(), flush=True)  # query
            visualizer_cb(visualizer.readline(), flush=True)  # answer

        # answer
        solution_cb(line, flush=False)
        for i in xrange(int(line)):
            solution_cb(solution.readline(), flush=False)
