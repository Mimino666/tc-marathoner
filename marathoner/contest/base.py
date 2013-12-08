class BaseContest(object):
    '''BaseContest is an abstract class for contest-specific modifications to
    Marathoner.
    '''
    def __init__(self, project):
        self.project = project
        self.maximize = project.maximize

    def extract_score(self, seed, visualizer_stdout, solution_stderr):
        '''Extract score and run time information.
        Return initialized Score object.

        @param seed: seed number of the test
        @type seed: int

        @param visualizer_stdout: output received from visualizer's stdout
        @type visualizer_stdout: list of lines

        @param solution_stderr: output received from solution's stderr
        @type solution_stderr: list of lines
        '''
        raise NotImplementedError()

    # single test callbacks
    def single_test_starting(self, seed):
        '''Called before running the single test.'''
        raise NotImplementedError()

    def single_test_ending(self, seed, visualizer_stdout, solution_stderr,
                           best_score, current_score):
        '''Called after the single test *successfully* finished.

        @param best_score: best score for the current test, until now.
                It has not been updated with current_score, so you can compare
                old data with the new one. Will be automatically updated after.
        @type best_score: Score

        @param current_score: score for the current test
        @type current_score: Score
        '''
        raise NotImplementedError()

    # multi-test callbacks
    def multiple_tests_starting(self, num_tests):
        '''Called before running the batch of tests.'''
        raise NotImplementedError()

    def one_test_starting(self, seed):
        '''Called before running the test from the batch.'''
        raise NotImplementedError()

    def one_test_ending(self, seed, visualizer_stdout, solution_stderr,
                        best_score, current_score):
        '''Called after the test from the batch *successfully* finished.'''
        raise NotImplementedError()

    def multiple_tests_ending(self, num_tests):
        '''Called after running the batch of tests.

        @param num_tests: number of tests that actually ran. Can be lower
                          than number of tests sent to `multiple_tests_starting()`,
                          if user kills execution.
        '''
        raise NotImplementedError()
