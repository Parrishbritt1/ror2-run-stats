import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import time
import datetime
from pytz import timezone


PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Risk of Rain 2\\Risk of Rain 2_Data\\RunReports\\History"
IMG_PATH = "C:\\Users\\Parrish\\Desktop\\Metamorphasis\\RoR2Dash"


def browse_files():
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Text files", "*.txt"), ("all files", ".")))
    label_file_explorer.configure(text="File Opened: "+filename)

def get_player_stats(path):
    tree = ET.parse(path)
    stat_dict = {}

    # Get player infos
    root = tree.getroot()
    for ele in root:
        if ele.tag == "playerInfos":
            player_infos = ele

    # Get stats sheet from player info
    for info in player_infos[0]:
        if info.tag == "bodyName":
            stat_dict["class"] = info.text
        
        if info.tag == "statSheet":
            player_stats = info
    
    # Get stats and assign them into a dictionary
    for stat in player_stats[0]:
        stat_dict[stat.tag] = stat.text

    return stat_dict

def get_avg_timeperstage(run_stats):
    avg_timeperstage = 0
    count = 0
    for run in run_stats:
        count += 1
        for stat in run:
            if "totalTimeAlive" in stat:
                min_alive = float(run[stat]) / 60
            elif "highestStagesCompleted" in stat:
                stages_completed = int(run[stat]) + 1
        
        avg_timeperstage += min_alive / stages_completed

    avg_timeperstage /= count
    return avg_timeperstage

def get_kills_against(run_stats):
    # Returns kills list and labels(names) list
    labels = []
    kills = []
    for run in run_stats:
        for stat in run:
            if "killsAgainst." in stat:
                if stat[13:] in labels:
                    idx = labels.index(stat[13:])
                    kills[idx] += int(run[stat])
                else:
                    labels.append(stat[13:])
                    kills.append(int(run[stat]))

    return kills, labels

def get_total_kills(run_stats):
    # Returns total kills among all runs
    total_kills = 0
    for run in run_stats:
        for stat in run:
            if "killsAs." in stat:
                total_kills += int(run[stat])
                break

    return total_kills

def get_longest_time_alive(run_stats):
    longest_time_alive = -99999999999
    for run in run_stats:
        for stat in run:
            if "totalTimeAlive" in stat:
                if float(run[stat]) > longest_time_alive:
                    longest_time_alive = float(run[stat])


    print(datetime.timedelta(seconds=longest_time_alive))

    print(longest_time_alive)
    # hour.minutes
    print(longest_time_alive / 3600)
    
    # if longest_time_alive / 3600 >= 1:
    #     return str(round(longest_time_alive/3600, 2))[:-3]+"h "+ str(longest_time_alive/3600*60)


    # minutes.seconds
    print(longest_time_alive / 3600 * 60)
    return str(round(longest_time_alive / 60, 2))+""


# Sort files in the ...\RunReports\History directory
# (Last element is the most recent)
os.chdir(PATH)
files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime, reverse=True)

run_stats = []
for f in files:
    run_stats.append(get_player_stats(PATH+"\\"+f))



def test():
    pass

root = tk.Tk()
root.title("RoR2Dash")
root.geometry("1200x800")
root.configure(bg="gray")

# File Browsing--------------------------------------------------
# label_file_explorer = tk.Label(root, text="Find ...\Risk of Rain 2\Risk of Rain 2_Data\RunReports\History")
# file_explore_button = tk.Button(root, text="...", command=browse_files)
# label_file_explorer.pack()
# file_explore_button.pack()


# SCROLLBAR-------------------------------------------------------------
# Create a main frame
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# Create a canvas
my_canvas = tk.Canvas(left_frame, bg="gray")
my_canvas.pack(side=tk.LEFT, fill=tk.Y)

# Add a scrollbar to the canvas
scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=my_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the canvas
my_canvas.configure(yscrollcommand=scrollbar.set)
my_canvas.bind("<Configure>", lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# Create another frame inside the canvas
second_frame = tk.Frame(my_canvas, bg="gray")

# Add the new frame to a window in the canvas
my_canvas.create_window((0,0), window=second_frame, anchor="nw")


# Load images-----------------------------------------------
commando_img = tk.PhotoImage(file=IMG_PATH+"\\commando.png")
huntress_img = tk.PhotoImage(file=IMG_PATH+"\\huntress.png")
bandit_img = tk.PhotoImage(file=IMG_PATH+"\\bandit.png")
mult_img = tk.PhotoImage(file=IMG_PATH+"\\mul-t.png")
engineer_img = tk.PhotoImage(file=IMG_PATH+"\\engineer.png")
artificer_img = tk.PhotoImage(file=IMG_PATH+"\\artificer.png")
mercenary_img = tk.PhotoImage(file=IMG_PATH+"\\mercenary.png")
rex_img = tk.PhotoImage(file=IMG_PATH+"\\rex.png")
loader_img = tk.PhotoImage(file=IMG_PATH+"\\loader.png")
acrid_img = tk.PhotoImage(file=IMG_PATH+"\\acrid.png")
captain_img = tk.PhotoImage(file=IMG_PATH+"\\captain.png")

idx = 0
for run in run_stats:
    class_body = run["class"]
    modTimesinceEpoc = os.path.getmtime(files[idx])
    run_dateandtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))

    if class_body == "Bandit2Body":
        tk.Button(second_frame, image=bandit_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "HuntressBody":
        tk.Button(second_frame, image=huntress_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "CaptainBody":
        tk.Button(second_frame, image=captain_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "EngiBody":
        tk.Button(second_frame, image=engineer_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "MercBody":
        tk.Button(second_frame, image=mercenary_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "MageBody":
        tk.Button(second_frame, image=artificer_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "CommandoBody":
        tk.Button(second_frame, image=commando_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "TreebotBody":
        tk.Button(second_frame, image=rex_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "ToolbotBody":
        tk.Button(second_frame, image=mult_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "CrocoBody":
        tk.Button(second_frame, image=acrid_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)
    elif class_body == "LoaderBody":
        tk.Button(second_frame, image=loader_img, text=" "*50 + run_dateandtime, compound="left", command=test, bg="gray").grid(row=idx, column=0, pady=10, padx=10)

    idx += 1


Overallstats_label = tk.Label(root, text="Overall Stats", font=("Verdana", 50), bg="gray", fg="#5500FF").pack()

total_kills = get_total_kills(run_stats)
total_kills_label = tk.Label(root, text="Total Kills: "+str(total_kills))
total_kills_label.pack()

longest_time_alive = get_longest_time_alive(run_stats)
longest_time_alive_label = tk.Label(root, text="Longest Time Alive "+longest_time_alive[:2]+"m "+longest_time_alive[3:]+"s")
longest_time_alive_label.pack()

# kills, labels = get_kills_against(run_stats)

# fig = Figure()
# plot1 = fig.add_subplot()
# plot1.barh(labels, kills)

# canvas = FigureCanvasTkAgg(fig, master=root)
# canvas.get_tk_widget().pack()


print(get_avg_timeperstage(run_stats))


root.mainloop()
