from itertools import chain
import re

from six import print_

from marathoner.contest.base import BaseContest
from marathoner.scores import Score


class Contest(BaseContest):
    score_re = re.compile(r'^\s*Score\s*=\s*(\d+(?:[.,]\d+)?)\s*$')

    # formating strings used for outputing multi-test data
    header = ('Seed', 'Score', 'Best', 'Relative', 'Run time')
    column_width = [5, 15, 15, 8, 8]
    row_format = '| %s |' %  ' | '.join('%%%ss' % l for l in column_width)
    hline = '|-%s-|' % '-|-'.join('-' * l for l in column_width)  # horizontal line

    def extract_score(self, visualizer_stdout, solution_stderr):
        for line in chain(visualizer_stdout, solution_stderr):
            score_match = self.score_re.match(line)
            if score_match:
                return float(score_match.group(1))

    def single_test_starting(self, seed):
        self.old_best_score = self.project.scores[seed].score
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
        if self.old_best_score and best_score.score != self.old_best_score:
            print_('\tBest score: %.2f (old: %.2f)' % (best_score.score, self.old_best_score))
        else:
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
        self.score_sum = 0.0
        self.zero_seeds = []

        self._write_line(self.hline)
        self._write_line(self.row_format % self.header)
        self._write_line(self.hline)

    def one_test_starting(self, seed):
        pass

    def one_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        if not current_score.score:
            self.zero_seeds.append(seed)
        relative = Score.relative_score(self.maximize, current_score, best_score)
        self.score_sum += relative
        data = (seed,
            '%.2f' % current_score.score,
            '%.2f' % best_score.score,
            '%.3f' % relative,
            '%.2f' % current_score.run_time)
        self._write_line(self.row_format % data)

    def _write_line(self, line):
        self.log_file.write(line + '\n')
        self.log_file.flush()
        print_(line)

    def multiple_tests_ending(self, num_tests):
        self._write_line(self.hline)
        self._write_line(self.row_format % self.header)
        self._write_line(self.hline)
        self._write_line('')
        self._write_line('Relative score on %s tests: %.5f' % (num_tests, self.score_sum))
        if num_tests:
            self._write_line('Average relative score: %.5f' % (self.score_sum / num_tests))
        if self.zero_seeds:
            self._write_line('You have scored zero points on %s seeds. Here are some of the seeds: %s' %
                   (len(self.zero_seeds), self.zero_seeds[:10]))
        self.log_file.close()
