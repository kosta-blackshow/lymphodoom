"""Headless play-test with the native engine: runs a script of key presses and
console commands under Xvfb and saves screenshots.

usage: python3 tools/playtest.py ENGINE WADDIR OUTDIR SCRIPT
SCRIPT lines:  wait <sec> | key <xdotool key> | hold <key> <sec> | type <text> | con <console command> | shot <name>
"""
import os
import subprocess
import sys
import time

engine, waddir, outdir, script = sys.argv[1:5]
extra = sys.argv[5:]
os.makedirs(outdir, exist_ok=True)
disp = ":%d" % (60 + os.getpid() % 30)
xv = subprocess.Popen(["Xvfb", disp, "-screen", "0", "800x600x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
env = dict(os.environ, DISPLAY=disp, SDL_AUDIODRIVER="dummy", HOME=waddir)
log = open(os.path.join(outdir, "log.txt"), "w")
game = subprocess.Popen(["stdbuf", "-oL", "-eL", engine, "-iwad", "lymphodoom.wad", "-width", "640", "-height", "400",
                         "-nomusic"] + extra, cwd=waddir, env=env, stdout=log, stderr=log)
time.sleep(3)


WID = None


def xdo(*a):
    global WID
    if WID is None:
        r = subprocess.run(["xdotool", "search", "--name", "."], env=env, capture_output=True, text=True).stdout.split()
        WID = r[-1] if r else None
    if WID and a[0] in ("key", "keydown", "keyup", "type", "mousedown"):
        subprocess.run(["xdotool", "windowactivate", "--sync", WID], env=env, stderr=subprocess.DEVNULL)
        subprocess.run(["xdotool", "windowfocus", "--sync", WID], env=env, stderr=subprocess.DEVNULL)
    subprocess.run(["xdotool"] + list(a), env=env)


wid = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", ""], env=env, capture_output=True, text=True).stdout.split()
for line in open(script):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    cmd, _, arg = line.partition(" ")
    if cmd == "wait":
        time.sleep(float(arg))
    elif cmd == "key":
        for k in arg.split():
            xdo("key", "--delay", "60", k)
            time.sleep(0.08)
    elif cmd == "hold":
        k, s = arg.split()
        xdo("keydown", k)
        time.sleep(float(s))
        xdo("keyup", k)
    elif cmd == "fire":
        xdo("mousedown", "1")
        time.sleep(float(arg))
        xdo("mouseup", "1")
    elif cmd == "type":
        xdo("type", "--delay", "70", arg)
    elif cmd == "con":
        xdo("key", "grave")
        time.sleep(0.3)
        xdo("type", "--delay", "40", arg)
        time.sleep(0.2)
        xdo("key", "Return")
        time.sleep(0.3)
    elif cmd == "shot":
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-video_size", "800x600", "-i", disp,
                        "-frames:v", "1", os.path.join(outdir, arg + ".png")], env=env)
    if game.poll() is not None:
        print("engine exited with", game.returncode)
        break
game.terminate()
time.sleep(0.5)
game.kill()
xv.terminate()
log.close()
print(open(os.path.join(outdir, "log.txt")).read()[-1500:])
