from itertools import chain
import re

from six import print_

from marathoner.contest.base import BaseContest
from marathoner.scores import Score


class Contest(BaseContest):
    score_re = re.compile(r'^Score\s*=\s*(\d+(?:\.\d+)?)\s*$')
    run_time_re = re.compile(r'^Run time\s*=\s*(\d+(?:\.\d+)?)\s*$')

    def extract_score(self, seed, visualizer_stdout, solution_stderr):
        score, run_time = None, 0.0
        for line in chain(visualizer_stdout, solution_stderr):
            score_match = self.score_re.match(line)
            if score_match:
                score = float(score_match.group(1))
            run_time_match = self.run_time_re.match(line)
            if run_time_match:
                run_time = float(run_time_match.group(1))
        if score is None:
            raise RuntimeError('Unable to extract score from seed %s' % seed)
        return Score(seed, score, run_time)

    def single_test_starting(self, seed):
        print_('Running single test %s...' % seed)

    def single_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        for line in visualizer_stdout:
            print_(line.rstrip())

        print_('\tRun time: %f' % current_score.run_time)
        print_('\tNew score: %f' % current_score.score)
        print_('\tBest score: %f' % best_score.score)
        print_('\tRelative score: %f' % self._get_relative_score(best_score, current_score))


    def multiple_tests_starting(self, num_tests):
        print_('Running %s tests...' % num_tests)
        log_filename = self.project.data_path('multiple_tests.log')
        self.log_file = open(log_filename, 'w')
        self.score_sum = 0

    def one_test_starting(self, seed):
        pass

    def one_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        relative = self._get_relative_score(best_score, current_score)
        self.score_sum += relative

        seed_str = 'Seed %s:' % seed
        score_str = 'Score: %.2f' % current_score.score
        best_str = 'Best: %.2f' % best_score.score
        relative_str = 'Rel.: %.3f' % relative
        run_time_str = 'Run time: %.2f' % current_score.run_time

        s = '%-10s %-17s %-16s %-13s %s' % (seed_str, score_str, best_str, relative_str, run_time_str)
        self.log_file.write(s + '\n')
        self.log_file.flush()
        print_(s)

    def multiple_tests_ending(self, num_tests):
        self.log_file.close()
        print_('Your relative score on %s tests is %.5f' % (num_tests, self.score_sum))

    def _get_relative_score(self, best_score, current_score):
        if not current_score.score:
            return 0.0
        if self.maximize:
            return current_score.score / max(best_score.score, best_score.score)
        else:
            return min(best_score.score, current_score.score) / current_score.score
