from itertools import chain
import re

from six import print_

from marathoner.contest.base import BaseContest
from marathoner.scores import Score


class Contest(BaseContest):
    score_re = re.compile(r'^Score\s*=\s*(\d+(?:\.\d+)?)\s*$')
    run_time_re = re.compile(r'^Run time\s*=\s*(\d+(?:\.\d+)?)\s*$')

    # formating strings used for outputing multi-test data
    header = ('Seed', 'Score', 'Best', 'Relative', 'Run time')
    column_len = [5, 15, 15, 8, 8]
    format = '| %s |' %  ' | '.join('%%%ss' % l for l in column_len)
    hl = '|-%s-|' % '-|-'.join('-' * l for l in column_len)  # horizontal line

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
        tag = self.project.current_tag
        if tag:
            print_('Running single test %s with tag "%s"...' % (seed, tag.name))
        else:
            print_('Running single test %s...' % seed)

    def single_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        for line in visualizer_stdout:
            print_(line.rstrip())

        print_('\tRun time: %.2f' % current_score.run_time)
        print_('\tNew score: %.2f' % current_score.score)
        print_('\tBest score: %.2f' % best_score.score)
        print_('\tRelative score: %.5f' % Score.relative_score(self.maximize, current_score, best_score))


    def multiple_tests_starting(self, num_tests):
        tag = self.project.current_tag
        if tag:
            print_('Running %s tests with tag "%s"...' % (num_tests, tag.name))
        else:
            print_('Running %s tests...' % num_tests)
        log_filename = self.project.data_path('multiple_tests.log')
        self.log_file = open(log_filename, 'w')
        self.score_sum = 0

        self._write_line('(+) means the absolute best score')
        self._write_line(self.hl)
        self._write_line(self.format % self.header)
        self._write_line(self.hl)

    def one_test_starting(self, seed):
        pass

    def one_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        relative = Score.relative_score(self.maximize, current_score, best_score)
        self.score_sum += relative

        if current_score.score == best_score.score:
            current_score_str = '(+) %.2f' % current_score.score
        else:
            current_score_str = '%.2f' % current_score.score

        data = (seed,
            current_score_str,
            '%.2f' % best_score.score,
            '%.3f' % relative,
            '%.2f' % current_score.run_time)
        self._write_line(self.format % data)

    def _write_line(self, line):
        self.log_file.write(line + '\n')
        self.log_file.flush()
        print_(line)

    def multiple_tests_ending(self, num_tests):
        self._write_line(self.hl)
        self.log_file.close()
        print_('Your relative score on %s tests is %.5f' % (num_tests, self.score_sum))
