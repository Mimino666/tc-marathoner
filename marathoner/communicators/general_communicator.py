from functools import partial

from marathoner.utils.async_reader import AsyncReader


class Communicator(object):
    def communicate(self, visualizer, solution, visualizer_cb, solution_cb):
        visualizer_input_reader = AsyncReader(visualizer, partial(visualizer_cb, flush=True))
        visualizer_input_reader.setDaemon(True)
        visualizer_input_reader.start()
        solution_output_reader = AsyncReader(solution, partial(solution_cb, flush=False))
        solution_output_reader.start()
        solution_output_reader.join()
