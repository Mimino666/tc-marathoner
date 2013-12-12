from os import path


class Score(object):
    '''Encapsulates score and run-time from the single test.'''
    def __init__(self, seed, score, run_time=None):
        self.seed = seed
        self.score = score
        self.run_time = run_time

    def __str__(self):
        return '<Test-%s Score: %s Time: %s>' % (self.seed, self.score, self.time)

    @classmethod
    def better(cls, maximize, score1, score2):
        '''Return better of the two scores.'''
        # zero score is always bad
        if not score1.score:
            return score2
        if not score2.score:
            return score1

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
    def __init__(self, project, scores_file):
        self.project = project
        self.scores_file = scores_file
        self.best_scores = {}
        # read scores from the file
        if path.exists(scores_file):
            with open(scores_file, 'r') as f:
                for line in f:
                    seed, score = line.split(':')
                    seed = int(seed)
                    score = float(score)
                    self.best_scores[seed] = Score(seed, score)
        else:
            # create empty file
            with open(scores_file, 'w') as f:
                pass

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
                f.write('%d: %f\n' % (score.seed, score.score))
