from psychopy import visual, event, core, gui
import random
import numpy as np
import csv
import os

# === Get Participant ID and Language Choice ===
dlg = gui.Dlg(title="Participant Info")
dlg.addField("Participant ID:")
dlg.addField("Language:", choices=["English", "Русский", "Қазақша"])
participant_info = dlg.show()

if dlg.OK and participant_info[0].strip():
    participant_id = participant_info[0].strip()
    language = participant_info[1]
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

# === Instruction texts in three languages ===
instruction_texts = {
    "English": (
        "Task-set switching\n\n"
        "You will be presented with either a letter or a number in each trial.\n"
        "Your task will depend on the shape that is displayed before the letter or number.\n"
        "There are two tasks:\n\n"
        "1. Letter Task (ellipse):\n"
        "   - Press 'left' if the letter is a vowel (A, E, I, O, U).\n"
        "   - Press 'right' if the letter is a consonant.\n\n"
        "2. Number Task (rectangle):\n"
        "   - Press 'left' if the number is odd.\n"
        "   - Press 'right' if the number is even.\n\n"
        "You will have 5 sample trials. Press any key to continue."
    ),
    "Русский": (
        "“Task-set switching”. В каждом испытании вам будет представлена либо буква, либо цифра.\n"
        "Ваша задача будет зависеть от фигуры, которая появляется перед буквой или цифрой.\n"
        "Есть два типа заданий:\n\n"
        "1. Задание с буквами (эллипс):\n"
        "   - Нажмите 'влево', если буква является гласной (A, E, I, O, U).\n"
        "   - Нажмите 'вправо', если буква согласная.\n\n"
        "2. Задание с цифрами (прямоугольник):\n"
        "   - Нажмите 'влево', если число нечетное.\n"
        "   - Нажмите 'вправо', если число четное.\n\n"
        "У вас будет 5 пробных испытаний. Нажмите любую клавишу, чтобы продолжить."
    ),
    "Қазақша": (
        "“Task-set switching”. Әр сынақта сізге әріп немесе сан беріледі.\n"
        "Тапсырмаңыз әріп немесе саннан бұрын көрсетілетін пішінге байланысты болады.\n"
        "Екі тапсырма бар:\n\n"
        "1. Әріп тапсырмасы (эллипс):\n"
        "   - Егер әріп дауысты дыбыс болса (A, E, I, O, U), 'сол' батырмасын басыңыз.\n"
        "   - Егер әріп дауыссыз дыбыс болса, 'оң' батырмасын басыңыз.\n\n"
        "2. Сан тапсырмасы (тіктөртбұрыш):\n"
        "   - Егер сан тақ болса, 'сол' батырмасын басыңыз.\n"
        "   - Егер сан жұп болса, 'оң' батырмасын басыңыз.\n\n"
        "Сізде 5 дайындыққа арналған мүмкіндік болады. Жалғастыру үшін кез келген батырманы басыңыз."
    )
}

# === Show selected language instructions ===
instruction_text = visual.TextStim(win, text=instruction_texts[language], color="white", height=0.07)

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
        
        explanation = {
            "English": (f"Your response was '{response_key}', "
                       f"The {correct_target_type} was {'odd' if correct_target_type == 'number' and correct_target_number % 2 == 1 else 'even' if correct_target_type == 'number' else 'a vowel' if correct_target_letter in 'AEIOU' else 'a consonant'}, "
                       f"the correct action was '{correct_target_label}'. "
                       f"Your answer was {'correct' if correct else 'incorrect'}."),
            "Русский": (f"Ваш ответ был '{'влево' if response_key == 'left' else 'вправо' if response_key == 'right' else 'нет ответа'}', "
                       f"{'Число было ' if correct_target_type == 'number' else 'Буква была '}"
                       f"{'нечётным' if correct_target_type == 'number' and correct_target_number % 2 == 1 else 'чётным' if correct_target_type == 'number' else 'гласной' if correct_target_letter in 'AEIOU' else 'согласной'}, "
                       f"правильное действие - {'нажать влево' if correct_response == 'left' else 'нажать вправо'}. "
                       f"Ваш ответ {'правильный' if correct else 'неправильный'}."),
            "Қазақша": (f"Сіздің жауабыңыз '{'сол' if response_key == 'left' else 'оң' if response_key == 'right' else 'жауап жоқ'}', "
                       f"{'Сан ' if correct_target_type == 'number' else 'Әріп '}"
                       f"{'тақ' if correct_target_type == 'number' and correct_target_number % 2 == 1 else 'жұп' if correct_target_type == 'number' else 'дауысты' if correct_target_letter in 'AEIOU' else 'дауыссыз'} болды, "
                       f"дұрыс әрекет - {'сол батырмасын басу' if correct_response == 'left' else 'оң батырмасын басу'}. "
                       f"Сіздің жауабыңыз {'дұрыс' if correct else 'қате'}.")
        }[language]

        feedback_text = {
            "English": "Sample Trial",
            "Русский": "Пробное испытание",
            "Қазақша": "Сынақ сынақ"
        }[language]

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

results_text = {
    "English": (f"Mean Reaction Time:\n"
               f"Switch Trials: {mean_rt_switch:.2f}\n"
               f"Non-Switch Trials: {mean_rt_non_switch:.2f}\n\n"
               f"Accuracy:\n"
               f"Switch Trials: {accuracy_switch:.2f}\n"
               f"Non-Switch Trials: {accuracy_non_switch:.2f}"),
    "Русский": (f"Среднее время реакции:\n"
               f"Смена задачи: {mean_rt_switch:.2f}\n"
               f"Без смены: {mean_rt_non_switch:.2f}\n\n"
               f"Точность:\n"
               f"Смена задачи: {accuracy_switch:.2f}\n"
               f"Без смены: {accuracy_non_switch:.2f}"),
    "Қазақша": (f"Орташа реакция уақыты:\n"
               f"Ауыстырылған тапсырма: {mean_rt_switch:.2f}\n"
               f"Ауыстырылмаған тапсырма: {mean_rt_non_switch:.2f}\n\n"
               f"Дәлдік:\n"
               f"Ауыстырылған тапсырма: {accuracy_switch:.2f}\n"
               f"Ауыстырылмаған тапсырма: {accuracy_non_switch:.2f}")
}[language]

results_display = visual.TextStim(win, text=results_text, color="white")
results_display.draw()
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