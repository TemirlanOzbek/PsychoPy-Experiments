from psychopy import visual, event, core
import random
import numpy as np

win = visual.Window(fullscr=True, color="black")
instructions = visual.TextStim(win, text="Press any key to start.", color="white")
instructions.draw()
win.flip()
event.waitKeys()

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

total_trials = num_trials * task_blocks

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

        response = event.waitKeys(maxWait=2.0, keyList=['left', 'right', 'escape'])

        if response is not None and 'escape' in response:
            win.close()
            core.quit()

        if response is None:
            response_key = None
            rt = None
        else:
            response_key = response[0]
            rt = core.getTime()

        correct_response = None

        if task_type == 'letter':
            correct_response = 'left' if letter in 'AEIOU' else 'right'
        else:
            correct_response = 'left' if number % 2 == 1 else 'right'

        if trial > 0:
            results.append({
                'block': block,
                'trial': trial,
                'task_type': task_type,
                'response': response_key,
                'correct': response_key == correct_response if response_key is not None else None,
                'rt': rt,
                'switch': switch_task
            })
        
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

results_text = visual.TextStim(win, text=f"Mean Reaction Time:\nSwitch Trials: {mean_rt_switch:.2f}\nNon-Switch Trials: {mean_rt_non_switch:.2f}\n\nAccuracy:\nSwitch Trials: {accuracy_switch:.2f}\nNon-Switch Trials: {accuracy_non_switch:.2f}", color="white")
results_text.draw()
win.flip()

event.waitKeys()
win.close()
core.quit()