import datetime
import os
import time
import tkinter as tk
from tkinter.constants import S
import tkinter.font as font
import xml.etree.ElementTree as ET
from tkinter import filedialog, ttk

import matplotlib.patches
import matplotlib.pyplot as plt
import pyglet
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from pytz import timezone

pyglet.font.add_file(os.getcwd()+"\\ror2-run-stats\\Bombardier-Regular.ttf")
PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Risk of Rain 2\\Risk of Rain 2_Data\\RunReports\\History"
IMG_PATH = os.getcwd()+"\\ror2-run-stats\images"
PURPLE = "#815DD5"
DARK_VIOLET = "#0B0033"
BLUE = "#00F2F2"
IVORY = "#F9F9ED"



def browse_files():
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Text files", "*.txt"), ("all files", ".")))
    label_file_explorer.configure(text="File Opened: "+filename)

def get_player_stats(path):
    """
    Parse through each stat within xml file and return a dictionary with
    xml tag as Key and xml text as Value 
    """
    # For parsing through xml documents
    tree = ET.parse(path)
    stat_dict = {}

    # Get player infos
    root = tree.getroot()
    for ele in root:
        if ele.tag == "runGuid":
            stat_dict["runGuid"] = ele.text

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
    """
    return the calculated average time in each stage of the game
    """
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

def get_player_played_amounts(run_stats):
    """
    Returns a dictionary of Key: class and Value: # of times played
    """
    labels = []
    values = []

    for run in run_stats:
        if run["class"] in labels:
            values[labels.index(run["class"])] += 1.0
        
        else:
            labels.append(run["class"])
            values.append(1.0)

    return labels, values

def get_kills_against(run_stats):
    """
    Returns 'kills' (list of the amount of kills), 'labels' (list containing the names of who is killed)
    """
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
    """
    Returns the total amount of kills over all runs
    """
    total_kills = 0
    for run in run_stats:
        for stat in run:
            if "killsAs." in stat:
                total_kills += int(run[stat])
                break

    return total_kills

def get_longest_time_alive(run_stats):
    """
    Returns the the run time with the longest time
    """
    longest_time_alive = -99999999999
    for run in run_stats:
        for stat in run:
            if "totalTimeAlive" in stat:
                if float(run[stat]) > longest_time_alive:
                    longest_time_alive = float(run[stat])


    # formats string from timedelta "0:21:32.92393" and returns it as "0h 21m 32s"
    time = datetime.timedelta(seconds=longest_time_alive)
    time_split = str(time).split(":")
    time_split.insert(2, time_split[-1][:2])
    time_split.pop(3)

    return time_split[0]+"h "+time_split[1]+"m "+time_split[2]+"s"

def seconds_to_hours(seconds):
    """
    Returns a converts seconds to string "0h 25m 29s" 

    ToDo: round seconds to two places 
    """ 
    hours = float(seconds) / 3600
    hours_arr = str(hours).split(".")
    str_hours = hours_arr[0]
    str_minutes = "."+hours_arr[1]
    float_minutes = float(str_minutes) * 60
    minute_arr = str(float_minutes).split(".")
    str_minutes = minute_arr[0]
    str_seconds = "."+minute_arr[1]
    float_seconds = float(str_seconds) * 60
    str_seconds = str(round(float_seconds, 2))

    return str_hours+"h " + str_minutes+"m "+ str_seconds+"s"

#  -------------FOR SCROLLING WHEN MOUSE IS IN THE LEFT FRAME------------
def on_mousewheel(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def bind_to_mousewheel(event, canvas):
    canvas.bind_all("<MouseWheel>", lambda e, canvas=canvas: on_mousewheel(e, canvas))

def unbind_to_mousewheel(event, canvas):
    canvas.unbind_all("<MouseWheel>")



def home_button_pressed(run):
    """
    Forget all frames and pack main_frame (Overall stats frame)
    """
    for frame in frames.values():
        frame.pack_forget()

    frames["main_frame"].pack(fill=tk.BOTH, expand=1)

def run_button_pressed(run, run_dateandtime):
    """ 
    Forget all frames and packs specific run frame with data widgets
    """

    for frame in frames.values():
        frame.pack_forget()

    frames[run["runGuid"]].pack(fill=tk.BOTH, expand=1)
    
    # This prevents packing of widgets multiple times 
    widgets = frames[run["runGuid"]].winfo_children()
    if not widgets:
        # ----------------------ROW 0----------------------------
        character = run["class"]
        class_img_label = tk.Label(frames[run["runGuid"]], image=class_img_dict[character], bg=DARK_VIOLET).grid(row=0, column=0)
        home_button = tk.Button(frames[run["runGuid"]], text="Home", font=("Bombardier", 20), compound="left", command=lambda run=run: home_button_pressed(run), bg=PURPLE, fg=BLUE).grid(row=0, column=1, padx=10)
        time_of_run_label = tk.Label(frames[run["runGuid"]], font=("Bombardier", 32), text="Run Date: " + run_dateandtime.split(" ")[0], bg=DARK_VIOLET, fg=PURPLE).grid(row=0, column=2)

        # ---------------------ROW 1----------------------------
        time_alive_label = tk.Label(frames[run["runGuid"]], text="Time alive: ", font=("Bombardier", 32), bg=DARK_VIOLET, fg=IVORY).grid(row=1, column=1, sticky="W")
        time_alive_stat_label = tk.Label(frames[run["runGuid"]], text=seconds_to_hours(run["totalTimeAlive"]), font=("Bombardier", 32), bg=DARK_VIOLET, fg=BLUE).grid(row=1, column=2, sticky="E")
        
        # ---------------------ROW 2----------------------------
        total_kills_label = tk.Label(frames[run["runGuid"]], text="Total kills: ", font=("Bombardier", 32), bg=DARK_VIOLET, fg=IVORY).grid(row=2, column=1, sticky="W")
        total_kills_stat_label = tk.Label(frames[run["runGuid"]], text=str(run["totalKills"]), font=("Bombardier", 32), bg=DARK_VIOLET, fg=BLUE).grid(row=2, column=2, sticky="E")

        # ---------------------ROW 3---------------------------
        total_gold_label = tk.Label(frames[run["runGuid"]], text="Total Gold: ", font=("Bombardier", 32), bg=DARK_VIOLET, fg=IVORY).grid(row=3, column=1, sticky="W")
        total_gold_stat_label = tk.Label(frames[run["runGuid"]], text=str(run["totalGoldCollected"]), font=("Bombardier", 32), bg=DARK_VIOLET, fg=BLUE).grid(row=3, column=2, sticky="E")
    

if __name__ == "__main__":
    root = tk.Tk()
    root.title("RoR2Dash")
    root.geometry("1200x800")
    root.configure(bg="gray")

    # Sort files in the ...\RunReports\History directory
    # (Last element is the most recent)
    os.chdir(PATH)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime, reverse=True)

    run_stats = []
    for f in files:
        run_stats.append(get_player_stats(PATH+"\\"+f))


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
    my_canvas = tk.Canvas(left_frame, bg=DARK_VIOLET)
    my_canvas.pack(side=tk.LEFT, fill=tk.Y)

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.bind("<Enter>", lambda e, my_canvas=my_canvas: bind_to_mousewheel(e, my_canvas))
    scrollbar.bind("<Leave>", lambda e, my_canvas=my_canvas: unbind_to_mousewheel(e, my_canvas))

    # Configure the canvas
    my_canvas.configure(yscrollcommand=scrollbar.set)
    my_canvas.bind("<Configure>", lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    my_canvas.bind("<Enter>", lambda e, my_canvas=my_canvas: bind_to_mousewheel(e, my_canvas))
    my_canvas.bind("<Leave>", lambda e, my_canvas=my_canvas: unbind_to_mousewheel(e, my_canvas))

    # Create another frame inside the canvas
    second_frame = tk.Frame(my_canvas, bg=DARK_VIOLET)
    second_frame.bind("<Enter>", lambda e, my_canvas=my_canvas: bind_to_mousewheel(e, my_canvas))
    second_frame.bind("<Leave>", lambda e, my_canvas=my_canvas: unbind_to_mousewheel(e, my_canvas))

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

    # Dictionary for tkinter buttons 
    class_img_dict = {"Bandit2Body": bandit_img, "HuntressBody": huntress_img, "CaptainBody": captain_img, "EngiBody": engineer_img,
                    "MercBody": mercenary_img, "MageBody": artificer_img, "CommandoBody": commando_img, "TreebotBody": rex_img,
                    "ToolbotBody": mult_img, "CrocoBody": acrid_img, "LoaderBody": loader_img}

    # Loop through each run and create a button for each one
    main_frame = tk.Frame(root, bg=DARK_VIOLET)
    main_frame.pack(fill=tk.BOTH, expand=1)

    frames = {"main_frame": main_frame}
    idx = 0
    for run in run_stats:
        class_body = run["class"]
        modTimesinceEpoc = os.path.getmtime(files[idx])
        run_dateandtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))

        frames[run["runGuid"]] = tk.Frame(root, bg=DARK_VIOLET)

        button = tk.Button(second_frame, image=class_img_dict[class_body], text=" "*50 + run_dateandtime, font=("Bombardier", 10), compound="left",
        command=lambda run=run, run_dateandtime=run_dateandtime: run_button_pressed(run, run_dateandtime), bg=PURPLE, fg=BLUE)
        button.grid(row=idx, column=0, pady=10, padx=10)
        idx += 1


    Overallstats_label = tk.Label(main_frame, text="Overall Stats", font=("Bombardier", 50), bg=DARK_VIOLET, fg=PURPLE).grid(row=0, column=0, columnspan=2)

    total_kills = get_total_kills(run_stats)
    total_kills_label = tk.Label(main_frame, text="Total Kills: ", font=("Bombardier", 28), bg=DARK_VIOLET, fg=IVORY).grid(row=1, column=0, sticky="W")
    total_kills_stat_label = tk.Label(main_frame, text=str(total_kills), font=("Bombardier", 28), bg=DARK_VIOLET, fg=BLUE).grid(row=1, column=0, sticky="E")

    longest_time_alive = get_longest_time_alive(run_stats)
    longest_time_alive_label = tk.Label(main_frame, text="Longest Time Alive: ", font=("Bombardier", 24), bg=DARK_VIOLET, fg=IVORY).grid(row=2, column=0, sticky="W")
    longest_time_alive_stat_label = tk.Label(main_frame, text=longest_time_alive, font=("Bombardier", 24), bg=DARK_VIOLET, fg=BLUE).grid(row=2, column=0, sticky="E")

    labels, values = get_player_played_amounts(run_stats)

    fig = Figure(figsize=(5,5))
    fig.patch.set_facecolor(DARK_VIOLET)
    ax = fig.add_subplot(111)
    ax.set_facecolor(DARK_VIOLET)
    ax.pie(values)
    ax.legend(labels, loc="best", bbox_to_anchor=(1, 1), borderaxespad=0)

    circle = matplotlib.patches.Circle((0,0), 0.5, color=DARK_VIOLET)
    ax.add_artist(circle)


    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.get_tk_widget().grid(row=3, column=0)
    

    
    root.mainloop()
