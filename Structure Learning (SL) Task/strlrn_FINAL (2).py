import os
from psychopy import visual, core, event, gui
import random
import csv
import numpy as np

# Multilingual instructions
instructions = {
    "English": {
        "welcome": (
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
        ),
        "practice_complete": "Now you will begin the MAIN task.\n\nEverything works the same as before, but you will NOT receive feedback after each response.\nTry to keep track of the patterns and predict as accurately as you can.\n\nPress any key to begin the main trials.",
        "complete": "Experiment complete!\n\nThank you for your participation.",
        "feedback": {
            "you_chose": "You chose:",
            "correct_answer": "The correct answer is:",
            "result_correct": "CORRECT!",
            "result_incorrect": "INCORRECT.",
            "result_text": "Your answer was {result}"
        }
    },
    "Қазақша": {
        "welcome": (
            "Экспериментке қош келдіңіз!\n\n"
            "Сіз символдар тізбегін бірінен соң бірі көресіз. Сіздің мақсатыңыз - байқаған үлгіңізге сүйене отырып, келесі ең ықтимал символды БОЛЖАУ.\n\n"
            "Әрбір тізбектің соңында 4 символ 2x2 торында пайда болады. Олардың бірін NUMPAD көмегімен таңдауыңыз керек:\n\n"
            "8 = Жоғарғы сол жақ (A символы)\n"
            "9 = Жоғарғы оң жақ (B символы)\n"
            "5 = Төменгі сол жақ (D символы)\n"
            "6 = Төменгі оң жақ (C символы)\n\n"
            "Ең ықтимал келесі символды таңдауға тырысыңыз!\n"
            "Жаттығу кезінде сіз кері байланыс және түсініктеме аласыз.\n\n"
            "Жаттығуларды бастау үшін кез келген пернені басыңыз."
        ),
        "practice_complete": "Енді сіз НЕГІЗГІ тапсырманы бастайсыз.\n\nБарлығы бұрынғыдай жұмыс істейді, бірақ әрбір жауаптан кейін сіз кері байланыс алмайсыз.\nҮлгілерді бақылап, мүмкіндігінше дәл болжауға тырысыңыз.\n\nНегізгі тапсырмаларды бастау үшін кез келген пернені басыңыз.",
        "complete": "Эксперимент аяқталды!\n\nҚатысқаныңыз үшін рахмет.",
        "feedback": {
            "you_chose": "Сіз таңдадыңыз:",
            "correct_answer": "Дұрыс жауап:",
            "result_correct": "ДҰРЫС!",
            "result_incorrect": "ҚАТЕ.",
            "result_text": "Сіздің жауабыңыз {result}"
        }
    },
    "Русский": {
        "welcome": (
            "Добро пожаловать в эксперимент!\n\n"
            "Вы будете видеть последовательность символов один за другим. Ваша цель - ПРЕДСКАЗАТЬ, какой символ, скорее всего, появится следующим, основываясь на наблюдаемой вами закономерности.\n\n"
            "В конце каждой последовательности появятся 4 символа в виде сетки 2x2. Вы должны выбрать один с помощью NUMPAD:\n\n"
            "8 = Верхний левый (Символ A)\n"
            "9 = Верхний правый (Символ B)\n"
            "5 = Нижний левый (Символ D)\n"
            "6 = Нижний правый (Символ C)\n\n"
            "Постарайтесь выбрать наиболее вероятный следующий символ!\n"
            "Во время тренировки вы будете получать обратную связь и объяснения.\n\n"
            "Нажмите любую клавишу, чтобы начать тренировочные испытания."
        ),
        "practice_complete": "Теперь вы начнете ОСНОВНОЕ задание.\n\nВсе работает так же, как и раньше, но вы НЕ будете получать обратную связь после каждого ответа.\nПостарайтесь отслеживать закономерности и предсказывать как можно точнее.\n\nНажмите любую клавишу, чтобы начать основные испытания.",
        "complete": "Эксперимент завершен!\n\nСпасибо за участие.",
        "feedback": {
            "you_chose": "Вы выбрали:",
            "correct_answer": "Правильный ответ:",
            "result_correct": "ПРАВИЛЬНЫМ!",
            "result_incorrect": "НЕПРАВИЛЬНЫМ.",
            "result_text": "Ваш ответ был {result}"
        }
    }
}
# === Experiment Settings ===
num_practice_trials = 5
num_blocks = 6
trials_per_block = 20
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
dlg.addField("Language:", choices=["English", "Қазақша", "Русский"])
participant_info = dlg.show()
if dlg.OK:
    participant_id = participant_info[0]
    language = participant_info[1]  # Store the selected language
else:
    core.quit()

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
data_file = os.path.join(data_dir, f"participant_{participant_id}.csv")

win = visual.Window(fullscr=True, color='black', units='height')
fixation = visual.TextStim(win, text='+', color='white', height=0.05)
data_log = []

### ИЗМЕНЕНИЕ: Добавлены переменные для отслеживания нажатия клавиш ###
escape_pressed = False
q_pressed = False

### ИЗМЕНЕНИЕ: Добавлена функция для проверки комбинации выхода ###
def check_for_quit():
    """Проверяет, были ли нажаты 'escape' и 'q' для выхода из эксперимента."""
    global escape_pressed, q_pressed
    keys = event.getKeys(keyList=['escape', 'q'])
    if 'escape' in keys:
        escape_pressed = True
    if 'q' in keys:
        q_pressed = True
    
    # Если обе клавиши были нажаты (не обязательно одновременно)
    if escape_pressed and q_pressed:
        win.close()
        core.quit()

def log_data(block, trial, last_symbol, response, correct, rt, true_next_symbol=None):
    """Extended to track both last shown symbol and true next symbol"""
    data_log.append([block, trial, last_symbol, response, correct, rt, true_next_symbol])

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
    # Во время ожидания тоже можно выйти
    keys = event.waitKeys(keyList=['escape', 'q', 'space', 'return']) # Ждем любую клавишу, но отслеживаем и выход
    check_for_quit()


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

def explain_response(true_next_symbol, response):
    """Fixed feedback function that uses the true correct answer"""
    lang = instructions[language]
    feedback = lang["feedback"]
    
    # --- STEP 1: Show what participant chose ---
    win.flip()
    text1 = visual.TextStim(win, text=feedback["you_chose"], pos=(0, 0.4), color='white', height=0.06)
    chosen_img = visual.ImageStim(win, image=image_paths.get(response, None), pos=(0, 0), size=(0.4, 0.4))
    text1.draw()
    if response in image_paths:
        chosen_img.draw()
    win.flip()
    event.waitKeys()
    check_for_quit() # Проверка выхода

    # --- STEP 3: Show correct answer ---
    win.flip()
    correct_title = visual.TextStim(win, text=feedback["correct_answer"], pos=(0, 0.4), color='white', height=0.06)
    correct_img = visual.ImageStim(win, image=image_paths[true_next_symbol], pos=(0, 0), size=(0.4, 0.4))
    correct_title.draw()
    correct_img.draw()
    win.flip()
    event.waitKeys()
    check_for_quit() # Проверка выхода

    # --- STEP 4: Final correctness message ---
    win.flip()
    result = feedback["result_correct"] if response == true_next_symbol else feedback["result_incorrect"]
    result_text = visual.TextStim(win, text=feedback["result_text"].format(result=result), pos=(0, 0), color='white', height=0.07)
    result_text.draw()
    win.flip()
    event.waitKeys()
    check_for_quit() # Проверка выхода

def show_text(text):
    explanation_text = visual.TextStim(win, text=text, color='white', height=0.045, wrapWidth=1.5)
    explanation_text.draw()
    win.flip()
    event.waitKeys()
    check_for_quit() # Проверка выхода

def run_trial(full_sequence, block, trial):
    """Modified to properly track last shown symbol and correct answer"""
    is_practice = (block == 0)
    timing = PRACTICE_TIMING if is_practice else TEST_TIMING
    
    event.clearEvents()
    
    sequence_to_show = full_sequence[:-1]
    true_next_symbol = full_sequence[-1]
    last_shown_symbol = sequence_to_show[-1] if sequence_to_show else full_sequence[0]

    for symbol in sequence_to_show:
        ### ИЗМЕНЕНИЕ: Замена старой проверки на новую функцию ###
        check_for_quit()
        
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
    
    event.clearEvents()
    core.wait(0.05)
    win.flip()

    timer = core.Clock()
    response = None
    response_pos = None
    rt = None

    while timer.getTime() < timing['max_response_time'] and response is None:
        ### ИЗМЕНЕНИЕ: Проверка выхода в цикле ожидания ответа ###
        check_for_quit()
        
        # Теперь getKeys ищет только нужные для ответа клавиши
        keys = event.getKeys(keyList=['num_8', 'num_9', 'num_5', 'num_6'])
        for key in keys:
            # Старая проверка на 'escape' убрана отсюда
            if key in response_map:
                response, _, response_pos = response_map[key]
                rt = timer.getTime()
                break

    correct = response == true_next_symbol
    log_data(block, trial, last_shown_symbol, response, correct, rt, true_next_symbol)

    file_exists = os.path.isfile(data_file)
    with open(data_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Block", "Trial", "LastSymbol", "Response", "Correct", "RT", 
                            "PI_Practice", "PI_Main", "ICD", "TrueNextSymbol"])
        writer.writerow([block, trial, last_shown_symbol, response, correct, rt, 
                        "", "", "", true_next_symbol])

    if response_pos:
        selected_marker = visual.Circle(win, radius=0.05, pos=response_pos, fillColor='white', lineColor='white')
        for stim in response_stims:
            stim.draw()
        selected_marker.draw()
        win.flip()
        core.wait(timing['feedback'])

    if is_practice:
        explain_response(true_next_symbol, response)

    if timing['iti'] > 0:
        fixation.draw()
        win.flip()
        core.wait(timing['iti'])

# === RUN EXPERIMENT ===
show_instructions(instructions[language]["welcome"])

for i in range(num_practice_trials):
    full_sequence = generate_sequence()
    run_trial(full_sequence, 0, i)

pi_practice = compute_pi(data_log, [0])
performance_text = visual.TextStim(win, text=f"You scored {pi_practice:.2f}% in the practice.", color='white', height=0.05)
performance_text.draw()
win.flip()
core.wait(3)
check_for_quit()

with open(data_file, 'r') as file:
    rows = list(csv.reader(file))
with open(data_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for row in rows:
        if row[0] == "0":
            row[6] = pi_practice
        writer.writerow(row)

show_instructions(instructions[language]["practice_complete"])

for block in range(1, num_blocks + 1):
    for trial in range(trials_per_block):
        full_sequence = generate_sequence()
        run_trial(full_sequence, block, trial)

# === Calculate PI ===
pi_initial = compute_pi(data_log, [1, 2])
pi_final = compute_pi(data_log, [5, 6])
pi_main = pi_final - pi_initial

# === Correct ICD Calculation ===
def compute_icd(data_log):
    optimal_choices = 0
    valid_trials = 0
    for trial in data_log:
        if trial[0] == 0:
            continue
        last_symbol = trial[2]
        if last_symbol is None: continue # Пропускаем пробы без последнего символа
        optimal_next = probabilities[last_symbol][0][0]
        if trial[3] is not None: # Учитываем только пробы с ответом
            if trial[3] == optimal_next:
                optimal_choices += 1
            valid_trials += 1
    return (optimal_choices / valid_trials) * 100 if valid_trials > 0 else 0

icd_score = compute_icd(data_log)

# === Show Results ===
result_text = visual.TextStim(win, text=f"PI: {pi_main:.2f}%\nICD: {icd_score:.2f}%", color='white', height=0.06)
result_text.draw()
win.flip()
core.wait(5)
check_for_quit()

# Save to CSV
with open(data_file, 'r') as file:
    rows = list(csv.reader(file))

with open(data_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for row in rows:
        if row[0] == "Block":
            writer.writerow(row)
            continue
            
        if row[0] == "0":
            if len(row) < 7: row.append(pi_practice)
            else: row[6] = pi_practice
            writer.writerow(row)
        else:
            if len(row) < 8: row.extend(["", ""])
            row[7] = pi_main
            if len(row) < 9: row.append("")
            row[8] = icd_score
            writer.writerow(row)

show_instructions(instructions[language]["complete"])
win.close()
core.quit()