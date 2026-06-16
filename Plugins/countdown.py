from src.MiddleManKit.MiddleMan import *
util.build()
import time

ask_t = Render("Enter the time in seconds").Input()
t = int(ask_t)
while t:
    mins, secs = divmod(t, 60)
    timer = '{:02d}:{:02d}'.format(mins, secs)
    print(timer, end="\r")
    time.sleep(1)
    t -= 1
Render('Your Countdown Has Ended', 'Countdown').Push()