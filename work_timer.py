import argparse
import os
import time
import tkinter
import tkinter.ttk
import winsound

from threading import Thread, Event

if os.path.exists("userConfiguration.py"):
    import userConfiguration  # type: ignore  # ignoring because it's the user's config and might or might not exist
    configurationDicts = userConfiguration.configurationDicts
else:
    configurationDicts: dict = {"default": {
                                    "pauseTime": "00:30:00",
                                    "workTime": "00:06:00",
                                    "maxOverTime": "00:30:00",
                                    "workTimeEndSound": "C:\\Windows\\Media\\Alarm02.wav",
                                    "overTimeEndSound": "C:\\Windows\\Media\\Alarm02.wav",
                                    "workTimeThreshold1": 0.75,
                                    "workTimeThreshold2": 0.9,
                                    "overTimeThreshold1": 0.75,
                                    "overTimeThreshold2": 0.9}}

argParser = argparse.ArgumentParser()
argParser.add_argument("-configuration",
                       type=str,
                       help="Configuration to use.",
                       default="default")
args = argParser.parse_args()
print("Used arguments are:")
print(args)
configurationDict = configurationDicts[args.configuration]


def overtimePbarLoop(overtimeSeconds: int, event: Event):
    for i in range(1, overtimeSeconds + 1):
        if event.is_set():
            print("overtimePbarLoop thread stopped by event.")
            break
        window.update_idletasks()
        overtimePbar["value"] += 1
        labelOverTimeOnBar["text"] = time.strftime("%H:%M:%S",
                                                   time.gmtime(i))
        if i == overtimeSeconds:
            winsound.PlaySound(configurationDict["overTimeEndSound"],
                               winsound.SND_FILENAME | winsound.SND_ASYNC)
        if i >= overtimeSeconds * configurationDict["overTimeThreshold2"]:
            labelOverTimeOnBar["background"] = "red"
        elif i >= overtimeSeconds * configurationDict["overTimeThreshold1"]:
            labelOverTimeOnBar["background"] = "yellow"
        time.sleep(1)
    print("overtimePbarLoop loop ended")
    overtimePbarEvent.clear()
    labelWorkTimeOnBar["background"] = originBackgroundColor
    labelOverTimeOnBar["background"] = originBackgroundColor
    buttonStart["text"] = "Start"


def workPbarLoop(workTimeSeconds: int, overtimeSeconds: int, event: Event):
    for i in range(1, workTimeSeconds + 1):
        if event.is_set():
            print("workPbarLoop thread stopped by event.")
            break
        window.update_idletasks()
        workPbar["value"] = i
        labelWorkTimeOnBar["text"] = time.strftime("%H:%M:%S",
                                                   time.gmtime(i))
        if i == workTimeSeconds:
            winsound.PlaySound(configurationDict["workTimeEndSound"],
                               winsound.SND_FILENAME | winsound.SND_ASYNC)
        if i >= workTimeSeconds * configurationDict["workTimeThreshold2"]:
            labelWorkTimeOnBar["background"] = "red"
        elif i >= workTimeSeconds * configurationDict["workTimeThreshold1"]:
            labelWorkTimeOnBar["background"] = "yellow"
        time.sleep(1)
    print("workPbarLoop thread ended")
    workPbarEvent.clear()
    if workPbar["value"] == workTimeSeconds:
        print("overtime starts")
        Thread(target=overtimePbarLoop, args=(overtimeSeconds, overtimePbarEvent)).start()


def startButtonClicked():
    if buttonStart["text"] == "Start":
        pauseSecondsStruct = time.strptime(entryPause.get(),
                                           "%H:%M:%S")
        pauseSeconds = pauseSecondsStruct.tm_hour * 3600 + pauseSecondsStruct.tm_min * 60 + pauseSecondsStruct.tm_sec
        workSecondsStruct = time.strptime(entryWorkTime.get(),
                                          "%H:%M:%S")
        workSeconds = workSecondsStruct.tm_hour * 3600 + workSecondsStruct.tm_min * 60 + workSecondsStruct.tm_sec
        totalSeconds = pauseSeconds + workSeconds
        print("Total seconds: {}".format(totalSeconds))

        overTimeSecondsStruct = time.strptime(entryOverTime.get(),
                                              "%H:%M:%S")
        overTimeSeconds = overTimeSecondsStruct.tm_hour * 3600 + overTimeSecondsStruct.tm_min * 60 + overTimeSecondsStruct.tm_sec
        print("Overtime seconds: {}".format(overTimeSeconds))

        workPbar["maximum"] = totalSeconds
        overtimePbar["maximum"] = overTimeSeconds

        Thread(target=workPbarLoop, args=(totalSeconds, overTimeSeconds, workPbarEvent)).start()
        buttonStart["text"] = "Stop"
    else:
        workPbarEvent.set()
        overtimePbarEvent.set()
        buttonStart["text"] = "Start"


# Create GUI
window = tkinter.Tk()
window.title("Work timer")
window.geometry("250x140")

labelStartTime = tkinter.Label(master=window,
                               text="Start time")
labelStartTime.grid(column=0,
                    row=0)

entryStartTime = tkinter.Entry(master=window)
entryStartTime.grid(column=1,
                    row=0)

labelPause = tkinter.Label(master=window,
                           text="Pause")
labelPause.grid(column=0,
                row=1)

entryPause = tkinter.Entry(master=window)
entryPause.grid(column=1,
                row=1)

labelWorkTime = tkinter.Label(master=window,
                              text="Work time")
labelWorkTime.grid(column=0,
                   row=2)

entryWorkTime = tkinter.Entry(master=window)
entryWorkTime.grid(column=1,
                   row=2)

labelOverTime = tkinter.Label(master=window,
                              text="Max. overtime")
labelOverTime.grid(column=0,
                   row=3)

entryOverTime = tkinter.Entry(master=window)
entryOverTime.grid(column=1,
                   row=3)

buttonStart = tkinter.Button(master=window,
                             text="Start",
                             command=startButtonClicked)
buttonStart.grid(column=0,
                 row=4,
                 columnspan=2)

workPbar = tkinter.ttk.Progressbar(master=window)
workPbar.grid(column=0,
              row=5)

labelWorkTimeOnBar = tkinter.Label(master=window,
                                   text="00:00:00")
labelWorkTimeOnBar.grid(column=0,
                        row=5)
originBackgroundColor = labelWorkTimeOnBar.cget("background")

overtimePbar = tkinter.ttk.Progressbar(master=window)
overtimePbar.grid(column=1,
                  row=5)

labelOverTimeOnBar = tkinter.Label(master=window,
                                   text="00:00:00")
labelOverTimeOnBar.grid(column=1,
                        row=5)

# Now set start time, pause time and end time based on config
entryStartTime.insert(index=0,
                      string=time.strftime("%H:%M:%S",
                                           time.localtime(time.time())))
entryPause.insert(index=0,
                  string=configurationDict["pauseTime"])
entryWorkTime.insert(index=0,
                     string=configurationDict["workTime"])
entryOverTime.insert(index=0,
                     string=configurationDict["maxOverTime"])

workPbarEvent = Event()
overtimePbarEvent = Event()

window.mainloop()
