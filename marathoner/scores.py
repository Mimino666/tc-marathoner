from os import path
import re


class Score(object):
    '''Encapsulates score and run-time of the single test.'''
    def __init__(self, seed, score, run_time=None):
        self.seed = int(seed)
        self.score = float(score)
        self.run_time = float(run_time or 0.0)

    def __str__(self):
        return '<Test-%s Score: %s Run time: %s>' % (self.seed, self.score, self.time)

    @classmethod
    def better(cls, maximize, score1, score2):
        '''Return better of the two scores.'''
        # zero score is always bad
        if not score1.score:
            return score2
        if not score2.score:
            return score1

        # for the same score, compare run times
        if score1.score == score2.score:
            if not score1.run_time:
                return score2
            if not score2.run_time:
                return score1
            return score1 if score1.run_time < score2.run_time else score2

        if maximize == (score1.score > score2.score):
            return score1
        else:
            return score2

    @classmethod
    def relative_score(cls, maximize, current_score, best_score):
        if not current_score.score:
            return 0.0
        if maximize:
            return current_score.score / max(best_score.score, best_score.score)
        else:
            return min(best_score.score, current_score.score) / current_score.score


class Scores(object):
    score_re = re.compile(r'^\D*(?P<seed>\d+(?:[,.]\d+)?)\D+(?P<score>\d+(?:[,.]\d+)?)(\D+(?P<time>\d+(?:[,.]\d+)?))?\D*$', re.IGNORECASE)

    def __init__(self, project, scores_file):
        self.project = project
        self.scores_file = scores_file
        self.best_scores = {}
        # read scores from the file
        if path.exists(scores_file):
            with open(scores_file, 'r') as f:
                for num, line in enumerate(f, 1):
                    match = self.score_re.match(line)
                    if match:
                        score = Score(
                            match.group('seed'),
                            match.group('score'),
                            match.group('time'))
                        self.best_scores[score.seed] = score
                    elif not line.isspace():
                        raise RuntimeError('Invalid line (%s) in "%s" score file:\n\t%s' % (num, scores_file, line))
        else:
            # create empty file
            with open(scores_file, 'w') as f:
                pass

    def __len__(self):
        return len(self.best_scores)

    def __getitem__(self, seed):
        return self.best_scores.get(seed, Score(seed, 0.0))

    def __setitem__(self, seed, score):
        score = Score.better(self.project.maximize, self[seed], score)
        self.best_scores[seed] = score

    @property
    def seeds(self):
        return self.best_scores.keys()

    def save(self):
        with open(self.scores_file, 'w') as f:
            for seed in sorted(self.seeds):
                score = self.best_scores[seed]
                f.write('Seed: %d \tScore: %f \tRun time: %f\n' % (score.seed, score.score, score.run_time))

    def update(self, scores):
        for seed in scores.seeds:
            self[seed] = Score.better(self.project.maximize, self[seed], scores[seed])
