from pid import PID
import math


FOV = 59 * math.pi / 180  # radians
LED_WIDTH = 3  # cm


class LedTracker:
    def __init__(self):
        self.lr_pid = PID(1, 0.8, 0.01)
        self.ud_pid = PID(1.5, 0.8, 0.01)
        self.fb_pid = PID(-1, -0.8, -0.01)
        self.fb_pid.set_point = 30

    def update(self, center, radius, img):
        height, width, _ = img.shape
        cm_to_px = LED_WIDTH / (radius * 2)

        lr_px_dist = width / 2 - center[0]
        lr_cm_dist = lr_px_dist * cm_to_px
        self.lr_pid.update(lr_cm_dist)

        ud_px_dist = center[1] - height / 2
        ud_cm_dist = ud_px_dist * cm_to_px
        self.ud_pid.update(ud_cm_dist)

        fraction_of_view = 2 * radius / width
        angle = FOV * fraction_of_view
        fb_cm_dist = LED_WIDTH / (2 * math.tan(angle / 2))
        print("calced dist", fb_cm_dist)
        self.fb_pid.update(fb_cm_dist)

        lr_out = round(self.lr_pid.output)
        ud_out = round(self.ud_pid.output)
        fb_out = round(self.fb_pid.output)

        return lr_out, fb_out, ud_out, 0
