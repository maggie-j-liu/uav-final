from pid import PID


class LedTracker:
    def __init__(self):
        self.lr_pid = PID(1, 0.8, 0.01)
        self.ud_pid = PID(1.5, 0.8, 0.01)

    def update(self, center, radius, img):
        cm_to_px = 3 / (radius * 2)

        lr_px_dist = img.shape[1] / 2 - center[0]
        lr_cm_dist = lr_px_dist * cm_to_px
        self.lr_pid.update(lr_cm_dist)

        ud_px_dist = center[1] - img.shape[0] / 2
        ud_cm_dist = ud_px_dist * cm_to_px
        self.ud_pid.update(ud_cm_dist)

        lr_out = round(self.lr_pid.output)
        ud_out = round(self.ud_pid.output)
        return lr_out, 0, ud_out, 0
