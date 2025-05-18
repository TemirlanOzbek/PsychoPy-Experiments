import subprocess
import json
import os
from psychopy import visual, event, core

# 🔹 List your task filenames here
tasks = [
    "Corsi/corsi_blocks_lastrun.py",
    "Flanker Test/attention_network_task_lastrun.py",
    "Stroop Task/stroop_lastrun.py",
    "Structure Learning/Str Lrn V2.py",
    "TMT/trail-making_lastrun.py",
    "WCST/Wisconsin Card Sorting Task_lastrun.py",
    "tss_instr.py"
]

progress_file = "progress.json"

def load_progress():
    # Always return -1 to start from the first task every time
    return -1

def save_progress(index):
    # Save progress (not necessary if we always start from the first task)
    with open(progress_file, "w") as f:
        json.dump({"last_completed": index}, f)

def show_break_screen(current_task_index, total_tasks):
    win = visual.Window(fullscr=False, color='black')
    message_text = (
        f"Task {current_task_index+1}/{total_tasks} completed\n\n"
        "Press ENTER to continue to next task\n"
        "Press R to restart this task\n"
        "Press ESC + DELETE to quit completely"
    )
    message = visual.TextStim(win, text=message_text, color='white', height=0.07, wrapWidth=1.5)
    message.draw()
    win.flip()

    while True:
        keys = event.getKeys()
        if 'return' in keys:  # Continue to next task
            win.close()
            return 'continue'
        elif 'r' in keys:  # Restart current task
            win.close()
            return 'restart'
        elif 'escape' in keys and 'delete' in keys:  # Emergency exit
            win.close()
            return 'exit'
        core.wait(0.1)

def run_pipeline():
    # Always start from the first task by setting last_completed to -1
    current_task_index = load_progress()
    total_tasks = len(tasks)

    while current_task_index < total_tasks:
        task = tasks[current_task_index]
        print(f"\n🔹 Starting {task}... (ESC = abort task, ESC + DELETE = emergency stop)")

        # Run task
        process = subprocess.Popen(["python", task])
        task_completed_normally = False

        try:
            while True:
                if process.poll() is not None:
                    # Task finished by itself
                    task_completed_normally = True
                    break

                # Check for key press
                keys = event.getKeys()
                if 'escape' in keys and 'delete' in keys:  # Emergency stop
                    print("\n⛔ Emergency stop (ESC + DELETE).")
                    process.terminate()
                    save_progress(current_task_index)
                    return
                elif 'escape' and 'q' in keys:  # Abort current task
                    print("\n⛔ Task aborted with ESC.")
                    process.terminate()
                    break

                core.wait(0.1)

        except KeyboardInterrupt:
            print("\n⛔ Manually interrupted.")
            process.terminate()
            save_progress(current_task_index)
            return

        if task_completed_normally:
            print(f"✅ {task} completed!\n")
            save_progress(current_task_index)
            
            # Show break screen with options
            result = show_break_screen(current_task_index, total_tasks)
            
            if result == 'continue':
                current_task_index += 1  # Move to next task
            elif result == 'restart':
                continue  # Will restart same task
            elif result == 'exit':
                print("🚪 Emergency stop after break. Progress saved.")
                return
        else:
            # Task was aborted, ask if user wants to restart
            win = visual.Window(fullscr=False, color='black')
            message = visual.TextStim(win, 
                text="Task was aborted\n\nPress R to restart\nPress ENTER to continue anyway\nESC+DELETE to quit", 
                color='white', height=0.07)
            message.draw()
            win.flip()
            
            while True:
                keys = event.getKeys()
                if 'r' in keys:
                    win.close()
                    break  # Will restart same task
                elif 'return' in keys:
                    win.close()
                    current_task_index += 1
                    break
                elif 'escape' in keys and 'delete' in keys:
                    win.close()
                    print("🚪 Emergency stop. Progress saved.")
                    return
                core.wait(0.1)

    print("\n🎉 All tasks completed!")
    if os.path.exists(progress_file):
        os.remove(progress_file)

if __name__ == "__main__":
    run_pipeline()