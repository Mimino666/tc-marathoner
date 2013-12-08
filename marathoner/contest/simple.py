from itertools import chain
import re

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
        print 'Running single test %s...' % seed

    def single_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        for line in visualizer_stdout:
            print line.rstrip()

        print '\tRun time: %f' % current_score.run_time
        print '\tNew score: %f' % current_score.score
        print '\tOld score: %f' % best_score.score

        if not best_score.score or not current_score.score:
            return

        if self.maximize:
            ratio = 100.0 * (current_score.score - best_score.score) / best_score.score
        else:
            ratio = 100.0 * (best_score.score - current_score.score) / best_score.score
        if ratio >= 0:
            print '\t+%.2f%% better' % ratio
        else:
            print '\t%.2f%% worse' % ratio


    def multiple_tests_starting(self, num_tests):
        print 'Running %s tests...' % num_tests
        log_filename = self.project.data_path('multiple_tests.log')
        self.log_file = open(log_filename, 'wb')

    def one_test_starting(self, seed):
        pass

    def one_test_ending(self, seed, visualizer_stdout, solution_stderr, best_score, current_score):
        seed_str = 'Seed %s:' % seed
        run_time_str = 'Run time: %.2f' % current_score.run_time

        if not best_score.score or not current_score.score:
            score_str = 'Score: %.2f' % current_score.score
        else:
            if self.maximize:
                ratio = 100.0 * (current_score.score - best_score.score) / best_score.score
            else:
                ratio = 100.0 * (best_score.score - current_score.score) / best_score.score

            if ratio >= 0:
                score_str = 'Score: %-9.2f (+%.2f%%)' % (current_score.score, ratio)
            else:
                score_str = 'Score: %-9.2f (%.2f%%)' % (current_score.score, ratio)

        s = '%-10s %-28s %s' % (seed_str, score_str, run_time_str)
        self.log_file.write(s + '\n')
        self.log_file.flush()
        print s

    def multiple_tests_ending(self, num_tests):
        self.log_file.close()
