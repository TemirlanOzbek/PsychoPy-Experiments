import os
from psychopy import visual, core, event, gui
import random
import csv
import numpy as np

# === Experiment Settings ===
num_practice_trials = 5
num_blocks = 3
trials_per_block = 40
symbols = ['A', 'B', 'C', 'D']
probabilities = {
    'A': [('B', 0.8), ('C', 0.2)],
    'B': [('C', 0.8), ('D', 0.2)],
    'C': [('D', 0.8), ('A', 0.2)],
    'D': [('A', 0.8), ('B', 0.2)],
}
image_paths = {symbol: f'resized{symbol}.png' for symbol in symbols}

dlg = gui.Dlg(title="Structure Learning Task")
dlg.addField("Participant ID:")
participant_info = dlg.show()
if dlg.OK:
    participant_id = participant_info[0]
else:
    core.quit()

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
data_file = os.path.join(data_dir, f"participant_{participant_id}.csv")

win = visual.Window(fullscr=True, color='black', units='height')
fixation = visual.TextStim(win, text='+', color='white', height=0.05)
data_log = []

def log_data(block, trial, symbol, response, correct, rt):
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
    'feedback': 0.3,
    'iti': 0.15,
    'max_response_time': 1.5
}

def explain_response(sequence, response):
    last_symbol = sequence[-2]
    correct_symbol = sequence[-1]
    prob_dict = dict(probabilities[last_symbol])
    response_img = image_paths.get(response, None)

    # --- STEP 1: Show what participant chose ---
    win.flip()
    text1 = visual.TextStim(win, text="You chose:", pos=(0, 0.4), color='white', height=0.06)
    chosen_img = visual.ImageStim(win, image=response_img, pos=(0, 0), size=(0.4, 0.4))
    text1.draw()
    if response_img:
        chosen_img.draw()
    win.flip()
    event.waitKeys()

    # --- STEP 2: Show real probabilities ---
#    win.flip()
 #   prob_title = visual.TextStim(win, text="The real probabilities are:", pos=(0, 0.45), color='white', height=0.06)
  #  prob_title.draw()

   # y_pos = 0.15
    #for sym, prob in probabilities[last_symbol]:
     #   sym_img = visual.ImageStim(win, image=image_paths[sym], pos=(-0.2, y_pos), size=(0.3, 0.3))
      #  prob_text = visual.TextStim(win, text=f"{int(prob*100)}%", pos=(0.2, y_pos), color='white', height=0.06)
       # sym_img.draw()
        #prob_text.draw()
       # y_pos -= 0.35

   # win.flip()
   # event.waitKeys()

    # --- STEP 3: Show correct answer ---
    win.flip()
    correct_title = visual.TextStim(win, text="The correct answer is:", pos=(0, 0.4), color='white', height=0.06)
    correct_img = visual.ImageStim(win, image=image_paths[correct_symbol], pos=(0, 0), size=(0.4, 0.4))
    correct_title.draw()
    correct_img.draw()
    win.flip()
    event.waitKeys()

    # --- STEP 4: Final correctness message ---
    win.flip()
    result = "CORRECT!" if response == correct_symbol else "INCORRECT."
    result_text = visual.TextStim(win, text=f"Your answer was {result}", pos=(0, 0), color='white', height=0.07)
    result_text.draw()
    win.flip()
    event.waitKeys()


def show_text(text):
    explanation_text = visual.TextStim(win, text=text, color='white', height=0.045, wrapWidth=1.5)
    explanation_text.draw()
    win.flip()
    event.waitKeys()

def run_trial(sequence, block, trial):
    is_practice = (block == 0)
    timing = PRACTICE_TIMING if is_practice else TEST_TIMING

    for symbol in sequence:
        if event.getKeys(['escape']) and event.getKeys(['q']):
            win.close()
            core.quit()
        stim = visual.ImageStim(win, image=image_paths[symbol], size=(0.5, 0.5))
        stim.draw()
        win.flip()
        core.wait(timing['stimulus'])

        fixation.draw()
        win.flip()
        core.wait(timing['isi'])

    red_dot = visual.TextStim(win, text='•', color='red', height=0.05)
    red_dot.draw()
    win.flip()
    core.wait(timing['end_cue'])

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
            if key == 'escape' and key == 'q' :
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
            writer.writerow(["Block", "Trial", "Symbol", "Response", "Correct", "RT", "PI_Practice", "PI_Main", "ICD"])
        writer.writerow([block, trial, sequence[-1], response, correct, rt, "", ""])

    if response_pos:
        selected_marker = visual.Circle(win, radius=0.05, pos=response_pos, fillColor='white', lineColor='white')
        for stim in response_stims:
            stim.draw()
        selected_marker.draw()
        win.flip()
        core.wait(timing['feedback'])

    if is_practice:
        explain_response(sequence, response)


    if timing['iti'] > 0:
        fixation.draw()
        win.flip()
        core.wait(timing['iti'])

# === RUN EXPERIMENT ===
show_instructions(
    "Welcome to the experiment!\n\n"
    "You will see a sequence of symbols one after another. Your goal is to PREDICT which symbol is most likely to come next, based on the pattern you observe.\n\n"
    "At the end of each sequence, 4 symbols will appear in a 2x2 grid. You must select one using your NUMPAD:\n\n"
    "8 = Top-left (Symbol A)\n"
    "9 = Top-right (Symbol B)\n"
    "5 = Bottom-left (Symbol D)\n"
    "6 = Bottom-right (Symbol C)\n\n"
    "Try your best to choose the most likely next symbol!\n"
    "During practice, you will get feedback and an explanation.\n\n"
    "Press any key to begin the practice trials."
)

for i in range(num_practice_trials):
    sequence = generate_sequence()
    run_trial(sequence, 0, i)

pi_practice = compute_pi(data_log, [0])
performance_text = visual.TextStim(win, text=f"You scored {pi_practice:.2f}% in the practice.", color='white', height=0.05)
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

show_instructions(
    "Now you will begin the MAIN task.\n\n"
    "Everything works the same as before, but you will NOT receive feedback after each response.\n"
    "Try to keep track of the patterns and predict as accurately as you can.\n\n"
    "Press any key to begin the main trials."
)

for block in range(1, num_blocks + 1):
    for trial in range(trials_per_block):
        sequence = generate_sequence()
        run_trial(sequence, block, trial)

# === Обновлённый расчёт PI ===
pi_initial = compute_pi(data_log, [1])       # Первый основной блок
pi_final = compute_pi(data_log, [2, 3])       # Два финальных блока
pi_main = pi_final - pi_initial

# === ICD Calculation ===
# Определяем самый вероятный символ (80%) после каждого предыдущего
transition_map = {'A': 'B', 'B': 'C', 'C': 'D', 'D': 'A'}
icd_trials = [row for row in data_log if row[0] != 0]  # только main task
maximize_choices = 0
valid_trials = 0

for i in range(1, len(icd_trials)):
    prev_symbol = icd_trials[i-1][2]
    expected = transition_map.get(prev_symbol)
    response = icd_trials[i][3]
    if response and expected:
        valid_trials += 1
        if response == expected:
            maximize_choices += 1

icd_score = (maximize_choices / valid_trials) * 100 if valid_trials > 0 else 0

# === Отображаем результат
result_text = visual.TextStim(win, text=f"PI: {pi_main:.2f}%\nICD: {icd_score:.2f}%", color='white', height=0.06)
result_text.draw()
win.flip()
core.wait(5)


# Сохраняем в CSV
with open(data_file, 'r') as file:
    rows = list(csv.reader(file))

with open(data_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for row in rows:
        if row[0] != "0":
            row[7] = pi_main
            if len(row) < 9:
                row.append(icd_score)
            else:
                row[8] = icd_score
            writer.writerow(row)



show_instructions("Experiment complete!\n\nThank you for your participation.")
win.close()
core.quit()
