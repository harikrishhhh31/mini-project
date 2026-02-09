import math
import time

class OneEuroFilter:
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=1.0, beta=0.0):
        self.t_prev = t0
        self.x_prev = x0
        self.dx_prev = dx0
        self.min_cutoff = min_cutoff
        self.beta = beta

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def __call__(self, t, x):
        t_e = t - self.t_prev
        if t_e <= 0.0: return self.x_prev

        dx = (x - self.x_prev) / t_e
        dx_hat = self.exponential_smoothing(self.smoothing_factor(t_e, 1), dx, self.dx_prev)

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self.smoothing_factor(t_e, cutoff)
        
        x_hat = self.exponential_smoothing(a, x, self.x_prev)

        self.t_prev = t
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        return x_hat

class PointFilter:
    def __init__(self, min_cutoff=0.01, beta=20.0):
        self.filter_x = None
        self.filter_y = None
        self.min_cutoff = min_cutoff
        self.beta = beta

    def process(self, x, y):
        t = time.time()
        if self.filter_x is None:
            self.filter_x = OneEuroFilter(t, x, min_cutoff=self.min_cutoff, beta=self.beta)
            self.filter_y = OneEuroFilter(t, y, min_cutoff=self.min_cutoff, beta=self.beta)
            return x, y
        return int(self.filter_x(t, x)), int(self.filter_y(t, y))
