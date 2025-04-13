import os   
from psychopy import visual, core, event, gui
import random
import csv
import numpy as np

# === Experiment Settings ===
num_practice_trials = 5
num_blocks = 7
trials_per_block = 56
symbols = ['A', 'B', 'C', 'D']
probabilities = {
    'A': [('B', 0.8), ('C', 0.2)],
    'B': [('C', 0.8), ('D', 0.2)], 
    'C': [('D', 0.8), ('A', 0.2)],
    'D': [('A', 0.8), ('B', 0.2)], 
}

# Image paths
image_paths = {symbol: f'resized{symbol}.png' for symbol in symbols}

# ----------------------
# Participant Info Dialog
# ----------------------
dlg = gui.Dlg(title="Structure Learning Task")
dlg.addField("Participant ID:")
participant_info = dlg.show()
if dlg.OK:
    participant_id = participant_info[0]
else:
    core.quit()

# === Create Data Directory ===
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

data_file = os.path.join(data_dir, f"participant_{participant_id}.csv")

# === Initialize Window ===
win = visual.Window(fullscr=True, color='black', units='height')
fixation = visual.TextStim(win, text='+', color='white', height=0.05)

data_log = []

def log_data(block, trial, symbol, response, correct, rt):
    global data_log
    data_log.append([block, trial, symbol, response, correct, rt])

def compute_pi(data_log, blocks):
    trials = [trial[4] for trial in data_log if trial[0] in blocks]
    return np.mean(trials) * 100 if trials else 0

def generate_sequence(length=10):
    sequence = [random.choice(symbols)]
    for _ in range(length - 1):
        next_symbol = random.choices(*zip(*probabilities[sequence[-1]]))[0]
        sequence.append(next_symbol)
    return sequence

def show_instructions(text):
    instruction_text = visual.TextStim(win, text=text, color='white', height=0.05, wrapWidth=1.5)
    instruction_text.draw()
    win.flip()
    event.waitKeys()
    
# Define timing constants
PRACTICE_TIMING = {
    'stimulus': 0.3,
    'isi': 0.5,
    'end_cue': 0.5,
    'feedback': 0.3,
    'iti': 0.15,
    'max_response_time': 2.0
}

TEST_TIMING = {
    'stimulus': 0.25,
    'isi': 0.25,
    'end_cue': 0.5,
    'feedback': 0.0,  # No feedback in test
    'iti': 0.0,
    'max_response_time': 1.5
}


def run_trial(sequence, block, trial):
    is_practice = (block == 0)
    timing = PRACTICE_TIMING if is_practice else TEST_TIMING

    for symbol in sequence:
        if event.getKeys(['escape']):
            win.close()
            core.quit()

        stim = visual.ImageStim(win, image=image_paths[symbol], size=(0.5, 0.5))
        stim.draw()
        win.flip()
        core.wait(timing['stimulus'])

        fixation.draw()
        win.flip()
        core.wait(timing['isi'])

    # Red dot cue
    red_dot = visual.TextStim(win, text='•', color='red', height=0.05)
    red_dot.draw()
    win.flip()
    core.wait(timing['end_cue'])

    # Show response options
    response_map = {
        'num_8': ('A', image_paths['A'], (-0.15, 0.15)),
        'num_9': ('B', image_paths['B'], (0.15, 0.15)),
        'num_6': ('C', image_paths['C'], (0.15, -0.15)),
        'num_5': ('D', image_paths['D'], (-0.15, -0.15))
    }

    response_stims = [visual.ImageStim(win, image=img, pos=pos, size=(0.3, 0.3)) for _, img, pos in response_map.values()]
    for stim in response_stims:
        stim.draw()
    win.flip()

    timer = core.Clock()
    response = None
    response_pos = None
    rt = None

    while timer.getTime() < timing['max_response_time'] and response is None:
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                win.close()
                core.quit()
            elif key in response_map:
                response, _, response_pos = response_map[key]
                rt = timer.getTime()
                break

    correct = response == sequence[-1]
    log_data(block, trial, sequence[-1], response, correct, rt)

    file_exists = os.path.isfile(data_file)
    with open(data_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Block", "Trial", "Symbol", "Response", "Correct", "RT", "PI_Practice", "PI_Main"])
        writer.writerow([block, trial, sequence[-1], response, correct, rt, "", ""])

    # Feedback (white circle) only in practice
    if is_practice and response_pos:
        selected_marker = visual.Circle(win, radius=0.05, pos=response_pos, fillColor='white', lineColor='white')
        for stim in response_stims:
            stim.draw()
        selected_marker.draw()
        win.flip()
        core.wait(timing['feedback'])

    # ITI
    if timing['iti'] > 0:
        fixation.draw()
        win.flip()
        core.wait(timing['iti'])


show_instructions("Welcome! Try to predict the next symbol. Press any key to continue.")
for i in range(num_practice_trials):
    sequence = generate_sequence()
    run_trial(sequence, 0, i)

pi_practice = compute_pi(data_log, [0])
performance_text = visual.TextStim(win, text=f"You scored {pi_practice:.2f}%", color='white', height=0.05)
performance_text.draw()
win.flip()
core.wait(3)

with open(data_file, 'r') as file:
    rows = list(csv.reader(file))
with open(data_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for row in rows:
        if row[0] == "0":
            row[6] = pi_practice
        writer.writerow(row)

show_instructions("Now, you will proceed to the main task. Stay focused!")

for block in range(1, num_blocks + 1):
    for trial in range(trials_per_block):
        sequence = generate_sequence()
        run_trial(sequence, block, trial)

pi_initial = compute_pi(data_log, [1, 2])
pi_final = compute_pi(data_log, [6, 7])
pi_main = pi_final - pi_initial

with open(data_file, 'r') as file:
    rows = list(csv.reader(file))
with open(data_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for row in rows:
        if row[0] != "0":
            row[7] = pi_main
        writer.writerow(row)

show_instructions("Experiment complete! Thank you for participating.")
win.close()
core.quit()