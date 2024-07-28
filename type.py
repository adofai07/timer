import cv2
import time
import winsound
import datetime
from PIL import Image, ImageFont, ImageDraw, ImageColor
from config import *

def hour_minute_second_millisecond():
    return list(map(int, datetime.datetime.now().strftime("%H/%M/%S").split("/"))) + [time.time() % 1]

timer_font = ImageFont.truetype(TIMER_FONT, TIMER_FONT_SIZE)
ms_font = ImageFont.truetype(TIMER_FONT, MILLISECOND_FONT_SIZE)
app_font = ImageFont.truetype(APP_FONT, APP_FONT_SIZE)
stick_font = ImageFont.truetype(TIMER_FONT, STICK_FONT_SIZE)

_img = Image.new("RGB", IMAGE_SIZE, ImageColor.getrgb(IMAGE_BG))
_draw = ImageDraw.Draw(_img)
_timer_msg = (
    F"{6969 // 3600 :02.0f}{TIME_SEP}{(6969 % 3600) // 60 :02.0f}{TIME_SEP}{6969 % 60 :02.0f}"
    if SHOW_SECONDS else
    F"{6969 // 3600 :02.0f}{TIME_SEP}{(6969 % 3600) // 60 :02.0f}"
)
curr_msg = "CURR "
tot_msg = " TOT "

assert len(curr_msg) == len(tot_msg)

_, _, w3, h3 = _draw.textbbox((0, 0), _timer_msg, font=timer_font)
_, _, wms, hms = _draw.textbbox((0, 0), "000", font=ms_font)
_, _, w1, h1 = _draw.textbbox((0, 0), curr_msg, font=stick_font)
_, _, w2, h2 = _draw.textbbox((0, 0), curr_msg + "-", font=stick_font)
num_sticks = (IMAGE_SIZE[0] - STICK_MARGIN * 2 - w1) // (w2 - w1)
_, _, w4, h4 = _draw.textbbox((0, 0), curr_msg + "-" * num_sticks, font=stick_font)

def make_image(idx: int, timer: int, milliseconds: int | bool, title: str, curr: float, tot: float) -> None:
    img = Image.new("RGB", IMAGE_SIZE, ImageColor.getrgb(IMAGE_BG))
    draw = ImageDraw.Draw(img)

    timer_msg = (
        F"{timer // 3600 :02.0f}{TIME_SEP}{(timer % 3600) // 60 :02.0f}{TIME_SEP}{timer % 60 :02.0f}"
        if SHOW_SECONDS else
        F"{timer // 3600 :02.0f}{TIME_SEP}{(timer % 3600) // 60 :02.0f}"
    )

    # _, _, w, h = draw.textbbox((0, 0), message, font=font)
    # draw.text(((W - w) / 2, (H - h) / 2), message, font=font, fill=fontColor)

    # _, _, w3, h3 = draw.textbbox((0, 0), timer_msg, font=timer_font)
    draw.text((TIMER_POS[0] - w3 / 2, TIMER_POS[1] - h3 / 2), timer_msg, font=timer_font, fill=ImageColor.getrgb(TIMER_FG))

    # _, _, wms, hms = draw.textbbox((0, 0), str(milliseconds).zfill(3), font=ms_font)
    if SHOW_MILLISECONDS:
        draw.text((TIMER_POS[0] + w3 / 2, TIMER_POS[1] + h3 / 2 - hms), str(milliseconds or "").zfill(3), font=ms_font, fill=ImageColor.getrgb(MILLISECOND_FG))

    _, _, w, h = draw.textbbox((0, 0), title, font=app_font)
    draw.text((CURRENT_TAB_POS[0] - w / 2, CURRENT_TAB_POS[1] - h / 2), title, font=app_font, fill=ImageColor.getrgb(APP_FG))

    # curr_msg = "CURR "
    # tot_msg = "TOT  "

    # assert len(curr_msg) == len(tot_msg)

    # _, _, w1, h1 = draw.textbbox((0, 0), curr_msg, font=stick_font)
    # _, _, w2, h2 = draw.textbbox((0, 0), curr_msg + "-", font=stick_font)
    # num_sticks = (IMAGE_SIZE[0] - STICK_MARGIN * 2 - w1) // (w2 - w1)

    # _, _, w4, h4 = draw.textbbox((0, 0), curr_msg + "-" * num_sticks, font=stick_font)
    draw.text((IMAGE_SIZE[0] / 2 - w4 / 2, CURR_Y_POS - h4 / 2), curr_msg, font=stick_font, fill=ImageColor.getrgb(APP_FG))
    draw.text((IMAGE_SIZE[0] / 2 - w4 / 2, TOT_Y_POS - h4 / 2), tot_msg, font=stick_font, fill=ImageColor.getrgb(APP_FG))

    for i in range(num_sticks):
        draw.text((IMAGE_SIZE[0] / 2 - w4 / 2 + w1 + (w2 - w1) * i, CURR_Y_POS - h4 / 2), "-", font=stick_font, fill=(ImageColor.getrgb(FILLED_STICK) if curr >= (i + 1) / num_sticks else ImageColor.getrgb(UNFILLED_STICK)))
        draw.text((IMAGE_SIZE[0] / 2 - w4 / 2 + w1 + (w2 - w1) * i, TOT_Y_POS - h4 / 2), "-", font=stick_font, fill=(ImageColor.getrgb(FILLED_STICK) if tot >= (i + 1) / num_sticks else ImageColor.getrgb(UNFILLED_STICK)))

    img.save(F"frames/f{idx}.png")

class Time:
    def __init__(
        self,
        name: str="Timer",
        hour: int=0,
        minute: int=0,
        second: int=0
    ):
        assert isinstance(name  , str)
        assert isinstance(hour  , int)
        assert isinstance(minute, int)
        assert isinstance(second, int)

        self.name = name
        self.time = hour * 3600 + minute * 60 + second
        self.nth = -1

class Blocker:
    def __init__(
        self,
        hour: int=0,
        minute: int=0,
        second: int=0
    ):
        assert isinstance(hour  , int)
        assert isinstance(minute, int)
        assert isinstance(second, int)

        self.hour = hour
        self.minute = minute
        self.second = second

        self.name = F"Blocker (~{hour :02.0f}:{minute :02.0f}:{second :02.0f})"
        self.time = 0

        self.until = hour * 3600 + minute * 60 + second * 1
        self.wait = None

class Timer:
    def __init__(
        self,
        *timers: Time | Blocker
    ):
        for i in timers:
            assert isinstance(i, (Time, Blocker))

        self.timers = timers
        self.n = sum(int(isinstance(i, Time)) for i in timers)
        self.tot = sum(i.time for i in timers)

        cnt = 0
        for i in timers:
            if isinstance(i, Time):
                cnt += 1
                i.nth = cnt

    def run(self):
        st = time.time()
        tot = self.tot
        curr = self.timers[0].time
        acc = 0
        idx = 0

        for i in range(int(1e100)):
            elapsed = time.time() - st
            st += elapsed

            if isinstance(self.timers[idx], Time):
                curr -= elapsed

                make_image(0, int(curr), int(curr * 1000) % 1000, self.timers[idx].name + F" ({self.timers[idx].nth} / {self.n})", 1 - curr / self.timers[idx].time, (acc + (self.timers[idx].time - curr)) / tot)

            if isinstance(self.timers[idx], Blocker):
                hmsm = hour_minute_second_millisecond()
                t = hmsm[0] * 3600 + hmsm[1] * 60 + hmsm[2] + hmsm[3]
                curr = self.timers[idx].until - t

                if curr < -BLOCKER_NEW_DAY_THRESHOLD:
                    curr += 86400

                if self.timers[idx].wait is None:
                    self.timers[idx].wait = curr

                make_image(0, int(curr), int(curr * 1000) % 1000, self.timers[idx].name, 1 - curr / self.timers[idx].wait, acc / tot)

            cv2.imshow("timer", cv2.imread("frames/f0.png"))

            if (s := cv2.waitKey(1) & 0xFF) == QUIT_KEY:
                cv2.destroyAllWindows()
                return
            
            if s == PAUSE_KEY:
                cv2.imshow("timer", cv2.imread("frames/paused.png"))

                while True:
                    elapsed = time.time() - st
                    st += elapsed

                    if (s := cv2.waitKey(1) & 0xFF) == QUIT_KEY:
                        cv2.destroyAllWindows()
                        return
                    
                    if s == PAUSE_KEY:
                        break


            if curr <= 0:
                acc += self.timers[idx].time
                idx += 1

                if idx == len(self.timers):
                    cv2.destroyAllWindows()
                    return

                if curr < -1:
                    curr = 0
                
                curr += self.timers[idx].time

                winsound.Beep(ALARM_FREQ, ALARM_DURATION)