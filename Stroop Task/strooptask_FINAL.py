#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modified Stroop Task with:
- 180 trials (75% congruent, 25% incongruent)
- Feedback for incorrect responses (X for 400ms + blank for 200ms)
- On-screen response key reminders
- Data analysis including Stroop costs
- Pandas-based data saving
"""

# --- Import packages ---
from psychopy import locale_setup, prefs, plugins, sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)
import numpy as np
import os
import sys
import psychopy.iohub as io
from psychopy.hardware import keyboard
import pandas as pd
from datetime import datetime

# --- Setup global variables ---
deviceManager = hardware.DeviceManager()
_thisDir = os.path.dirname(os.path.abspath(__file__))
psychopyVersion = '2024.2.4'
expName = 'stroop'

# Translations dictionary
TRANSLATIONS = {
    'English': {
        'welcome': "Welcome to the Stroop Task!\n\n"
                   "Identify the COLOR of the letters (ignore the word):\n"
                   "LEFT = RED | DOWN = GREEN | RIGHT = BLUE\n\n"
                   "You MUST keep your eyes fixed directly on the word on the screen. DO NOT LOOK AWAY OR USE YOUR PERIPHERAL VISION, as this will invalidate the results of the task. Please focus on the center of the screen and respond as quickly and accurately as possible.\n\n"
                   "Press any key to begin.",
        'reminder': "LEFT = RED | DOWN = GREEN | RIGHT = BLUE",
        'feedback': "X",
        'thanks': "Experiment complete!\n\nThank you.",
        'keys': {
            'left': 'red',
            'down': 'green',
            'right': 'blue'
        }
    },
    'Kazakh': {
        'welcome': "Строп тапсырмасына қош келдіңіз!\n\n"
                  "Әріптердің ТҮСІН анықтаңыз (сөзді елемеңіз):\n"
                  "СОЛ = ҚЫЗЫЛ | ТӨМЕН = ЖАСЫЛ | ОҢ = КӨК\n\n"
                  "сіз КӨЗҚАРАСЫҢЫЗДЫ экрандағы сөзге тікелей тігіп отыруыңыз МІНДЕТТІ. КӨЗДІ БАСӨА ЖАӨӨА АУДАРМАҢЫЗ НЕМЕСЕ ШЕТКІ КӨРУДІ ҚОЛДАНБАҢЫЗ, себебі бұл тапсырма нәтижелерін жарамсыз етеді. Экран ортасына назар аударып, мүмкіндігінше жылдам әрі дәл жауап беріңіз.\n\n"
                  "Бастау үшін кез келген пернені басыңыз.",
        'reminder': "СОЛ = ҚЫЗЫЛ | ТӨМЕН = ЖАСЫЛ | ОҢ = КӨК",
        'feedback': "X",
        'thanks': "Эксперимент аяқталды!\n\nРахмет.",
        'keys': {
            'left': 'қызыл',
            'down': 'жасыл',
            'right': 'көк'
        }
    },
    'Russian': {
        'welcome': "Добро пожаловать в задание Струпа!\n\n"
                  "Определите ЦВЕТ букв (игнорируя слово):\n"
                  "ЛЕВАЯ = КРАСНЫЙ | ВНИЗ = ЗЕЛЕНЫЙ | ПРАВАЯ = СИНИЙ\n\n"
                  "Вы ОБЯЗАТЕЛЬНО должны держать взгляд сфокусированным прямо на слове на экране. НЕ ОТВОДИТЕ ВЗГЛЯД И НЕ ИСПОЛЬЗУЙТЕ БОКОВОЕ ЗРЕНИЕ, так как это сделает результаты задания недействительными. Пожалуйста, сфокусируйтесь на центре экрана и отвечайте как можно быстрее и точнее.\n\n"
                  "Нажмите любую клавишу для начала.",
        'reminder': "ЛЕВАЯ = КРАСНЫЙ | ВНИЗ = ЗЕЛЕНЫЙ | ПРАВАЯ = СИНИЙ",
        'feedback': "X",
        'thanks': "Эксперимент завершен!\n\nСпасибо.",
        'keys': {
            'left': 'красный',
            'down': 'зеленый',
            'right': 'синий'
        }
    }
}

COLORS = {
    # English
    'red': (1, -1, -1),
    'green': (-1, 1, -1),
    'blue': (-1, -1, 1),
    # Kazakh
    'қызыл': (1, -1, -1),
    'жасыл': (-1, 1, -1),
    'көк': (-1, -1, 1),
    # Russian
    'красный': (1, -1, -1),
    'зеленый': (-1, 1, -1),
    'синий': (-1, -1, 1)
}

# Experiment info
expInfo = {
    'participant': '',
    'session': '001',
    'language': ['English', 'Kazakh', 'Russian'],
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Setup window ---
def setupWindow(expInfo=None, win=None):
    win = visual.Window(
        size=[1536, 864], fullscr=True, screen=0,
        winType='pyglet', allowGUI=True, allowStencil=False,
        monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
        units='height'
    )
    return win

# --- Trial parameters ---
N_TRIALS = 180
CONGRUENT_RATIO = 0.75

# --- Create trial list ---
def create_trial_list():
    lang = expInfo['language']
    color_names = list(TRANSLATIONS[lang]['keys'].values())
    
    trials = []
    n_congruent = int(N_TRIALS * CONGRUENT_RATIO)
    
    for _ in range(n_congruent):
        color = np.random.choice(color_names)
        trials.append({
            'text': color.upper(),
            'letterColor': color,
            'congruent': 1
        })
    
    n_incongruent = N_TRIALS - n_congruent
    for _ in range(n_incongruent):
        word_color, ink_color = np.random.choice(color_names, 2, replace=False)
        trials.append({
            'text': word_color.upper(),
            'letterColor': ink_color,
            'congruent': 0
        })
    
    np.random.shuffle(trials)
    return trials

# --- Main experiment ---
def runExperiment():
    win = setupWindow()
    lang = expInfo['language']

    instrText = visual.TextStim(win, text=TRANSLATIONS[lang]['welcome'], height=0.05, wrapWidth=1.5)
    reminder = visual.TextStim(win, text=TRANSLATIONS[lang]['reminder'], pos=(0, -0.4), height=0.04)
    wordStim = visual.TextStim(win, height=0.25)
    feedback = visual.TextStim(win, text=TRANSLATIONS[lang]['feedback'], height=0.2, color='red')
    
    trials = create_trial_list()
    results = []
    
    instrText.draw()
    win.flip()
    event.waitKeys()
    
    # ### СОЗДАЕМ ТАЙМЕР ЗДЕСЬ, ОДИН РАЗ ###
    trial_clock = core.Clock()

    for trial in trials:
        wordStim.text = trial['text']
        wordStim.color = COLORS[trial['letterColor']]
        corrAns = [k for k, v in TRANSLATIONS[lang]['keys'].items() if v == trial['letterColor']][0]
        
        wordStim.draw()
        reminder.draw()
        
        # ### НАЧАЛО ИСПРАВЛЕНИЯ ###
        # Сбрасываем таймер и показываем стимул В ОДИН МОМЕНТ
        win.callOnFlip(trial_clock.reset) 
        event.clearEvents(eventType='keyboard')
        
        win.flip() # Стимул на экране, таймер пошел!
        
        # Ждем ответа
        keys = event.waitKeys(keyList=list(TRANSLATIONS[lang]['keys'].keys()) + ['escape'])
        
        # Получаем ПРАВИЛЬНОЕ время реакции
        reaction_time = trial_clock.getTime()
        
        if keys:
            resp = keys[0]
            if resp == 'escape':
                win.close()
                core.quit()
        else:
            resp = None
            reaction_time = None # Если вдруг waitKeys прервется
        # ### КОНЕЦ ИСПРАВЛЕНИЯ ###
        
        correct = int(resp == corrAns)
        
        trial_data = {
            'trial_num': len(results) + 1,
            'text': trial['text'],
            'letterColor': trial['letterColor'],
            'congruent': trial['congruent'],
            'response': resp,
            'correct': correct,
            'rt': reaction_time, # ЗАПИСЫВАЕМ ПРАВИЛЬНОЕ RT
        }
        results.append(trial_data)
        
        if not correct:
            feedback.draw()
            reminder.draw()
            win.flip()
            core.wait(0.4)
            reminder.draw()
            win.flip()
            core.wait(0.2)
        else:
            reminder.draw()
            win.flip()
            core.wait(0.2)
    
    save_data(results)
    
    thanks = visual.TextStim(win, text=TRANSLATIONS[lang]['thanks'], height=0.05)
    thanks.draw()
    win.flip()
    core.wait(2.0)
    win.close()

# --- Data analysis and saving ---
def save_data(results):
    df = pd.DataFrame(results)
    
    # ВАЖНО: Фильтрация теперь будет работать с секундами, а не с миллисекундами
    valid_rts = df[(df['rt'] > 0.300) & (df['correct'] == 1)].copy()
    if len(valid_rts) > 1:
        rt_mean = valid_rts['rt'].mean()
        rt_std = valid_rts['rt'].std()
        valid_rts = valid_rts[
            (valid_rts['rt'] > (rt_mean - 2.5 * rt_std)) & 
            (valid_rts['rt'] < (rt_mean + 2.5 * rt_std))
        ]
    
    congruent = df[df['congruent'] == 1]
    incongruent = df[df['congruent'] == 0]
    
    congruent_valid = valid_rts[valid_rts['congruent'] == 1]
    incongruent_valid = valid_rts[valid_rts['congruent'] == 0]
    
    summary = {
        'Participant': [expInfo['participant']],
        'total_trials': len(df),
        'n_congruent': len(congruent),
        'n_incongruent': len(incongruent),
        'mean_acc_congruent': congruent['correct'].mean(),
        'mean_acc_incongruent': incongruent['correct'].mean(),
        'mean_rt_congruent': congruent_valid['rt'].mean() if len(congruent_valid) > 0 else None,
        'mean_rt_incongruent': incongruent_valid['rt'].mean() if len(incongruent_valid) > 0 else None,
        'stroop_acc_cost': congruent['correct'].mean() - incongruent['correct'].mean(), # Accuracy cost is reversed
        'stroop_rt_cost': (incongruent_valid['rt'].mean() - congruent_valid['rt'].mean()) if (len(incongruent_valid) > 0 and len(congruent_valid) > 0) else None,
    }
    
    output_dir = os.path.join(_thisDir, 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stroop_{expInfo['participant']}_{timestamp}"
    
    df.to_excel(os.path.join(output_dir, f"{filename}_trial_data.xlsx"), index=False)
    summary_df = pd.DataFrame(summary)
    summary_df.to_excel(os.path.join(output_dir, f"{filename}_summary.xlsx"), index=False)

# --- Run experiment ---
if __name__ == '__main__':
    dlg = gui.DlgFromDict(expInfo, title=expName)
    if not dlg.OK:
        core.quit()
    
    runExperiment()