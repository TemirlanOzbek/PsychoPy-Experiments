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
    "WCST/Wisconsin Card Sorting Task_lastrun.py"
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

def show_break_screen():
    win = visual.Window(fullscr=False, color='black')
    message = visual.TextStim(win, text="You can take a break now.\n\nPress ENTER to continue to the next task.\n\nPress ESC + DELETE to stop everything.", color='white', height=0.07, wrapWidth=1.5)
    message.draw()
    win.flip()

    while True:
        keys = event.getKeys()
        if 'return' in keys:  # If Enter is pressed, continue to the next task
            break
        elif 'escape' in keys and 'delete' in keys:  # If ESC + DELETE is pressed, exit
            win.close()
            return 'exit'
        core.wait(0.1)

    win.close()
    return 'continue'

def run_pipeline():
    # Always start from the first task by setting last_completed to -1
    last_completed = load_progress()

    # Start the task from the beginning (skip no tasks)
    for i, task in enumerate(tasks):
        print(f"\n🔹 Starting {task}... (ESC = pause task, ESC + DELETE = emergency stop)")

        while True:
            # Run task
            process = subprocess.Popen(["python", task])

            try:
                while True:
                    if process.poll() is not None:
                        break  # Task finished normally

                    # Check for key press (ESC to pause, ESC + DELETE to emergency stop)
                    keys = event.getKeys()
                    if 'escape' in keys:  # If ESC is pressed, interrupt the task
                        print("\n⛔ Task interrupted with ESC.")
                        process.terminate()
                        save_progress(i)  # Save progress (stay on current task)
                        # Show break screen and wait for Enter to continue to the next task
                        result = show_break_screen()
                        if result == 'exit':  # If ESC + DELETE pressed, exit the pipeline
                            print("🚪 Emergency stop after break. Progress saved.")
                            return
                        print("\n🔹 Restarting the task from the beginning...")  # Restart the task
                        break  # Break to restart the task

                    elif 'escape' in keys and 'delete' in keys:  # If ESC + DELETE is pressed, exit the pipeline
                        print("\n⛔ Emergency stop (ESC + DELETE).")
                        process.terminate()
                        save_progress(i)
                        return

                    core.wait(0.1)

            except KeyboardInterrupt:
                print("\n⛔ Manually interrupted.")
                process.terminate()
                save_progress(i)
                return

            print(f"✅ {task} completed!\n")
            save_progress(i)

            # Show break screen after task is completed
            result = show_break_screen()
            if result == 'exit':  # If ESC + DELETE pressed, exit the pipeline
                print("🚪 Emergency stop after break. Progress saved.")
                return

    print("\n🎉 All tasks completed!")
    if os.path.exists(progress_file):
        os.remove(progress_file)

if __name__ == "__main__":
    run_pipeline()
