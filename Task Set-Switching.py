from psychopy import visual, event, core, gui
import random
import numpy as np
import csv
import os

# === Get Participant ID ===
dlg = gui.Dlg(title="Participant Info")
dlg.addField("Participant ID:")
participant_info = dlg.show()

if dlg.OK and participant_info[0].strip():
    participant_id = participant_info[0].strip()
else:
    core.quit()

# === Create data directory ===
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# === Set path to save data ===
data_file = os.path.join(data_dir, f"task_set_switching_{participant_id}.csv")

# === Create CSV file with header ===
with open(data_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Block", "Trial", "Task Type", "Response", "Correct", "Reaction Time", "Switch"])

win = visual.Window(fullscr=True, color="black")


instruction_text = visual.TextStim(win, text=(
    "Task-set switching\n\n"
    "You will be presented with either a letter or a number in each trial.\n"
    "Your task will depend on the shape that is displayed before the letter or number.\n"
    "There are two tasks:\n\n"
    "1. Letter Task (circle):\n"
    "   - Press 'left' if the letter is a vowel (A, E, I, O, U).\n"
    "   - Press 'right' if the letter is a consonant.\n\n"
    "2. Number Task (square):\n"
    "   - Press 'left' if the number is odd.\n"
    "   - Press 'right' if the number is even.\n\n"
    "You will have 5 sample trials. Press any key to continue."
), color="white", height=0.07)

instructions_done = False
while not instructions_done:
    instruction_text.draw()
    win.flip()
    keys = event.waitKeys()
    if keys:
        instructions_done = True

letters = ['A', 'E', 'I', 'O', 'U', 'C', 'F', 'T', 'X']
numbers = list(range(1, 10))
num_trials = 49
task_blocks = 4
switch_ratio = 1 / 3

results = []
correct_switch = 0
correct_non_switch = 0
total_switch = 0
total_non_switch = 0

def get_task_type(cue):
    return 'letter' if cue == 'circle' else 'number'

def training_trials():
    for i in range(5):
        cue = random.choice(['circle', 'square'])
        task_type = get_task_type(cue)

        correct_target_letter = random.choice(letters)
        correct_target_number = random.choice(numbers)

        if task_type == 'letter':
            correct_response = 'left' if correct_target_letter in 'AEIOU' else 'right'
        else:
            correct_response = 'left' if correct_target_number % 2 == 1 else 'right'

        cue_stim = visual.Circle(win, radius=0.1, fillColor=None, lineColor='white', lineWidth=1) if cue == 'circle' else visual.ShapeStim(
            win, vertices=[(-0.1, -0.05), (0.1, -0.05), (0.1, 0.05), (-0.1, 0.05)], fillColor=None, lineColor='white', lineWidth=1)
        cue_stim.draw()
        win.flip()
        core.wait(0.3)

        letter_stim = visual.TextStim(win, text=correct_target_letter, pos=(0, 0.2), color='white')
        number_stim = visual.TextStim(win, text=str(correct_target_number), pos=(0, -0.2), color='white')
        letter_stim.draw()
        number_stim.draw()
        win.flip()

        trial_clock = core.Clock()
        response = event.waitKeys(maxWait=2.0, keyList=['left', 'right', 'escape', 'q'])

        if response is not None and 'escape' and 'q' in response:
            win.close()
            core.quit()

        response_key = response[0] if response else None

        correct = response_key == correct_response if response_key is not None else None
        correct_target_label = 'left arrow key' if correct_response == 'left' else 'right arrow key'
        correct_target_type = 'letter' if task_type == 'letter' else 'number'
        feedback_text = "Sample Trial"
        
        explanation = (f"Your response was '{response_key}', "
                       f"The {correct_target_type} was {'odd' if correct_target_type == 'number' and correct_target_number % 2 == 1 else 'even' if correct_target_type == 'number' else 'a vowel' if correct_target_letter in 'AEIOU' else 'a consonant'}, "
                       f"the correct action was '{correct_target_label}'. "
                       f"Your answer was {'correct' if correct else 'incorrect'}.")
        
        feedback_display = visual.TextStim(win, text=feedback_text, color="white", pos=(0, 0.3), height=0.07)
        explanation_text = visual.TextStim(win, text=explanation, color="white", pos=(0, -0.1))

        feedback_display.draw()
        explanation_text.draw()
        win.flip()

        event.waitKeys()

training_trials()

for block in range(task_blocks):
    block_text = visual.TextStim(win, text=f"Block {block + 1}", color="white")
    block_text.draw()
    win.flip()
    core.wait(2)

    for trial in range(num_trials):
        current_trial = block * num_trials + trial
        last_task = results[-1]['task_type'] if results else None
        switch_task = (last_task is not None) and (random.random() < switch_ratio)
        cue = 'circle' if (switch_task and last_task == 'number') or (last_task is None and random.random() < 0.5) else 'square'
        task_type = get_task_type(cue)
        letter = random.choice(letters)
        number = random.choice(numbers)

        cue_stim = visual.ShapeStim(win, vertices=[(-0.1, -0.05), (0.1, -0.05), (0.1, 0.05), (-0.1, 0.05)], fillColor=None, lineColor='white', lineWidth=1) if cue == 'square' else visual.Circle(win, radius=0.1, fillColor=None, lineColor='white', lineWidth=1)
        cue_stim.draw()
        win.flip()
        core.wait(0.3)

        letter_stim = visual.TextStim(win, text=letter, pos=(0, 0.2), color='white')
        number_stim = visual.TextStim(win, text=str(number), pos=(0, -0.2), color='white')
        letter_stim.draw()
        number_stim.draw()
        win.flip()

        trial_clock = core.Clock()
        response = event.waitKeys(maxWait=2.0, keyList=['left', 'right', 'escape', 'q'])

        if response is not None and 'escape' and 'q' in response:
            win.close()
            core.quit()

        if response is None:
            response_key = None
            rt = None
        else:
            response_key = response[0]
            rt = trial_clock.getTime()

        correct_response = 'left' if (task_type == 'letter' and letter in 'AEIOU') or (task_type == 'number' and number % 2 == 1) else 'right'

        if trial > 0:
            trial_data = {
                'block': block,
                'trial': trial,
                'task_type': task_type,
                'response': response_key,
                'correct': response_key == correct_response if response_key is not None else None,
                'rt': rt,
                'switch': switch_task
            }

            results.append(trial_data)

            # Save this trial immediately
            with open(data_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    trial_data['block'],
                    trial_data['trial'],
                    trial_data['task_type'],
                    trial_data['response'],
                    trial_data['correct'],
                    f"{trial_data['rt']:.3f}" if trial_data['rt'] is not None else "",
                    trial_data['switch']
                ])

            if switch_task:
                total_switch += 1
                if response_key == correct_response:
                    correct_switch += 1
            else:
                total_non_switch += 1
                if response_key == correct_response:
                    correct_non_switch += 1

        fixation = visual.TextStim(win, text='+', color='white', pos=(0, 0))
        fixation.draw()
        win.flip()
        core.wait(random.choice([1.7, 1.825, 1.95]))

accuracy_switch = correct_switch / total_switch if total_switch > 0 else 0
accuracy_non_switch = correct_non_switch / total_non_switch if total_non_switch > 0 else 0

mean_rt_switch = np.mean([result['rt'] for result in results if result['switch'] and result['rt'] is not None])
mean_rt_non_switch = np.mean([result['rt'] for result in results if not result['switch'] and result['rt'] is not None])

results_text = visual.TextStim(win, text=(
    f"Mean Reaction Time:\n"
    f"Switch Trials: {mean_rt_switch:.2f}\n"
    f"Non-Switch Trials: {mean_rt_non_switch:.2f}\n\n"
    f"Accuracy:\n"
    f"Switch Trials: {accuracy_switch:.2f}\n"
    f"Non-Switch Trials: {accuracy_non_switch:.2f}"
), color="white")
results_text.draw()
win.flip()
event.waitKeys()

# === Save final summary ===
with open(data_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Mean Reaction Time (Switch Trials)", f"{mean_rt_switch:.2f}"])
    writer.writerow(["Mean Reaction Time (Non-Switch Trials)", f"{mean_rt_non_switch:.2f}"])
    writer.writerow(["Accuracy (Switch Trials)", f"{accuracy_switch:.2f}"])
    writer.writerow(["Accuracy (Non-Switch Trials)", f"{accuracy_non_switch:.2f}"])

win.close()
core.quit()