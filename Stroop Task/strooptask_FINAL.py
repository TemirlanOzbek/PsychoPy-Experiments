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
    'қызыл': (1, -1, -1),    # red
    'жасыл': (-1, 1, -1),    # green
    'көк': (-1, -1, 1),      # blue
    # Russian
    'красный': (1, -1, -1),  # red
    'зеленый': (-1, 1, -1),  # green
    'синий': (-1, -1, 1)     # blue
}

# Experiment info
expInfo = {
    'participant': '',
    'session': '001',
    'language': ['English', 'Kazakh', 'Russian'],  # Add this line
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
CONGRUENT_RATIO = 0.75  # 75% congruent trials



# --- Create trial list ---
def create_trial_list():
    lang = expInfo['language']
    color_names = list(TRANSLATIONS[lang]['keys'].values())  # Gets colors in selected language
    
    trials = []
    n_congruent = int(N_TRIALS * CONGRUENT_RATIO)
    
    # Create congruent trials (word and color match)
    for _ in range(n_congruent):
        color = np.random.choice(color_names)
        trials.append({
            'text': color.upper(),
            'letterColor': color,  # Now uses the language-specific color name
            'congruent': 1
        })
    
    # Create incongruent trials (word and color differ)
    n_incongruent = N_TRIALS - n_congruent
    for _ in range(n_incongruent):
        word_color, ink_color = np.random.choice(color_names, 2, replace=False)
        trials.append({
            'text': word_color.upper(),
            'letterColor': ink_color,  # Uses language-specific color name
            'congruent': 0
        })
    
    np.random.shuffle(trials)
    return trials

# --- Main experiment ---
def runExperiment():
    # Setup window and stimuli
    win = setupWindow()
    globalClock = core.Clock()
    
    # Get selected language
    lang = expInfo['language']

    # Instruction screen (using translations)
    instrText = visual.TextStim(win, 
        text=TRANSLATIONS[lang]['welcome'],
        height=0.05, wrapWidth=1.5)
    
    # Response reminder (stays on screen)
    reminder = visual.TextStim(win,
        text=TRANSLATIONS[lang]['reminder'],
        pos=(0, -0.4), height=0.04)
    
    # Stimulus and feedback
    wordStim = visual.TextStim(win, height=0.15)
    feedback = visual.TextStim(win, text=TRANSLATIONS[lang]['feedback'], height=0.2, color='red')
    
    # Create trials
    trials = create_trial_list()
    
    # Data storage
    results = []
    
    # Show instructions
    instrText.draw()
    win.flip()
    event.waitKeys()
    
    # Main trial loop
    for trial in trials:
        # Set up trial
        wordStim.text = trial['text']
        wordStim.color = COLORS[trial['letterColor']]
        corrAns = [k for k, v in TRANSLATIONS[lang]['keys'].items() if v == trial['letterColor']][0]
        
        # Present stimulus
        wordStim.draw()
        reminder.draw()
        win.flip()
        
        # ### НАЧАЛО ИСПРАВЛЕНИЯ ###
        event.clearEvents(eventType='keyboard')  # Clear any previous key presses
        
        # Wait for a single valid key press and get its timestamp
        keys = event.waitKeys(
            keyList=list(TRANSLATIONS[lang]['keys'].keys()) + ['escape'],
            timeStamped=True
        )
        
        # Process the single response
        if keys:
            resp, rt = keys[0]  # Unpack the first (and only) key press
            if resp == 'escape':
                win.close()
                core.quit()
        else:
            # This case is unlikely with waitKeys, but good practice to have
            resp = None
            rt = None
        # ### КОНЕЦ ИСПРАВЛЕНИЯ ###
        
        # Check accuracy
        correct = int(resp == corrAns)
        
        # Store trial data
        trial_data = {
            'trial_num': len(results) + 1,
            'text': trial['text'],
            'letterColor': trial['letterColor'],
            'congruent': trial['congruent'],
            'response': resp,
            'correct': correct,
            'rt': rt * 1000 if rt is not None else None,
        }
        results.append(trial_data)
        
        # Feedback for incorrect responses
        if not correct:
            feedback.draw()
            reminder.draw()
            win.flip()
            core.wait(0.4)
            
            # Blank screen
            reminder.draw()
            win.flip()
            core.wait(0.2)
        else:
            # Add a brief pause after correct trials for consistent timing
            reminder.draw()
            win.flip()
            core.wait(0.2)
    
    # Save data with pandas
    save_data(results)
    
    # Thank you screen
    thanks = visual.TextStim(win, text=TRANSLATIONS[lang]['thanks'], height=0.05)
    thanks.draw()
    win.flip()
    core.wait(2.0)
    win.close()

# --- Data analysis and saving ---
def save_data(results):
    df = pd.DataFrame(results)
    
    # Filter valid RTs (300ms < RT < 2.5SD from mean)
    valid_rts = df[(df['rt'] > 300) & (df['correct'] == 1)].copy()
    if len(valid_rts) > 1:
        rt_mean = valid_rts['rt'].mean()
        rt_std = valid_rts['rt'].std()
        valid_rts = valid_rts[
            (valid_rts['rt'] > (rt_mean - 2.5 * rt_std)) & 
            (valid_rts['rt'] < (rt_mean + 2.5 * rt_std))
        ]
    
    # Calculate summary statistics
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
        'stroop_acc_cost': incongruent['correct'].mean() - congruent['correct'].mean(),
        'stroop_rt_cost': (incongruent_valid['rt'].mean() - congruent_valid['rt'].mean()) if (len(incongruent_valid) > 0 and len(congruent_valid) > 0) else None,
    }
    
    # Create output directory if needed
    output_dir = os.path.join(_thisDir, 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save trial-by-trial data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stroop_{expInfo['participant']}_{timestamp}"
    
    df.to_excel(os.path.join(output_dir, f"{filename}_trial_data.xlsx"), index=False)
    
    # Save summary statistics
    summary_df = pd.DataFrame(summary)
    summary_df.to_excel(os.path.join(output_dir, f"{filename}_summary.xlsx"), index=False)

# --- Run experiment ---
if __name__ == '__main__':
    # Show dialog to get participant info
    dlg = gui.DlgFromDict(expInfo, title=expName)
    if not dlg.OK:
        core.quit()
    
    runExperiment()