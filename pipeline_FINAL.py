import os
import sys
import subprocess
from psychopy import visual, event, core

tasks = [
    "Corsi/corsi_blocks_FINAL.py",
    "Flanker Test/attention_network_task_FINAL.py",
    "Stroop Task/strooptask_FINAL.py",
    "Structure Learning/strlrn_FINAL (2).py",
    "TMT/tmt_FINAL.py",
    "WCST/wsc_FINAL.py",
    "Tss/tss_FINAL.py"
]

def show_break_screen(current_task_index, total_tasks):
    win = visual.Window(fullscr=False, color='black')
    message_text = (
        f"Task {current_task_index+1}/{total_tasks} completed\n\n"
        "Press ENTER to continue to next task\n"
        "Press R to restart this task\n"
        "Press ESC + Q to quit completely"
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
        elif 'escape' in keys and 'q' in keys:  # Quit
            win.close()
            return 'exit'
        core.wait(0.1)

def run_tasks():
    total_tasks = len(tasks)
    current_task_index = 0
    
    while current_task_index < total_tasks:
        task = tasks[current_task_index]
        print(f"\nStarting task: {task}")
        
        try:
            # Get the directory where the task script is located
            task_dir = os.path.dirname(task)
            # Change to that directory before running
            os.chdir(task_dir)
            
            # Run the task (now in the correct folder)
            process = subprocess.Popen(
                [sys.executable, os.path.basename(task)]  # Only the filename, not full path
            )
            
            # Monitor for key presses during task execution
            task_completed_normally = False
            while True:
                if process.poll() is not None:
                    task_completed_normally = True
                    break

                keys = event.getKeys()
                if 'escape' in keys and 'q' in keys:  # Emergency quit
                    print("\nEmergency stop (ESC + Q).")
                    process.terminate()
                    return
                elif 'escape' in keys:  # Abort current task
                    print("\nTask aborted (ESC).")
                    process.terminate()
                    break

                core.wait(0.1)
            
            # Return to the original directory
            os.chdir("..")
            
            if task_completed_normally:
                print(f"Completed task: {task}")
                result = show_break_screen(current_task_index, total_tasks)
                
                if result == 'continue':
                    current_task_index += 1
                elif result == 'restart':
                    continue
                elif result == 'exit':
                    print("Exiting early.")
                    return
            else:
                # Handle task abortion (restart/continue/quit)
                win = visual.Window(fullscr=False, color='black')
                message = visual.TextStim(win,
                    text="Task aborted\n\n[R] Restart\n[ENTER] Continue\n[ESC+Q] Quit",
                    color='white', height=0.07)
                message.draw()
                win.flip()
                
                while True:
                    keys = event.getKeys()
                    if 'r' in keys:
                        win.close()
                        break  # Restart same task
                    elif 'return' in keys:
                        win.close()
                        current_task_index += 1
                        break
                    elif 'escape' in keys and 'q' in keys:
                        win.close()
                        print("Emergency quit.")
                        return
                    core.wait(0.1)
                    
        except Exception as e:
            print(f"Unexpected error with {task}: {e}")
            os.chdir("..")  # Make sure we return to original directory on error
            current_task_index += 1  # Move to next task on error

    print("\nAll tasks completed!")

if __name__ == "__main__":
    run_tasks()