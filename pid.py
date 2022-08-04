import time


class PID:
    def __init__(self, P, I, D):
        self.k_p = P
        self.k_i = I
        self.k_d = D

        self.sample_time = 0.0
        self.last_time = time.time()

        self.set_point = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
        self.last_error = 0.0
        self.output = 0

    def update(self, feedback_value):
        error = self.set_point - feedback_value
        current_time = time.time()
        dt = current_time - self.last_time
        if dt >= self.sample_time:
            self.p_term = error
            self.i_term = error * dt
            if dt > 0:
                self.d_term = (error - self.last_error) / dt
            self.last_time = current_time
            self.last_error = error
            self.output = (self.k_p * self.p_term) + \
                (self.k_i * self.i_term) + (self.k_d * self.d_term)
