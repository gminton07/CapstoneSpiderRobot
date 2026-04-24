#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import os, signal, subprocess
import shlex

class GuiLauncher():
    def __init__(self, root):
        self.root = root
        self.root.title('GUI Launcher')
        self.root.geometry("250x400")
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

        ## Constants
        PADX = 15
        PADY = 10

        ## Variables
        self.core_var = tk.BooleanVar()
        self.sensor_var = tk.BooleanVar()
        self.gui_var = tk.BooleanVar()
        self.joy_var = tk.BooleanVar()

        ## Process variables
        self.loc_proc = None
        self.remote_proc = None

        ## Pi checkboxes
        pi_frame = tk.LabelFrame(root, text="PI")
        pi_frame.pack(padx=PADX, pady=PADY, fill='both', expand=True)

        tk.Checkbutton(pi_frame, text="Enable Core Group", variable=self.core_var).pack()


        ## Laptop checkboxes
        laptop_frame = tk.LabelFrame(root, text='Laptop')
        laptop_frame.pack(padx=PADX, pady=PADY, fill='both', expand=True)

        tk.Checkbutton(laptop_frame, text="Enable GUI Group", variable=self.gui_var).pack()
        
        ## Control checkboxes
        control_frame = tk.LabelFrame(root, text='Control Group')
        control_frame.pack(padx=PADX, pady=PADY, fill='both', expand=True)
        tk.Checkbutton(control_frame, text="Enable Sensor Group", variable=self.sensor_var, command=self.toggle_sensor).pack()
        tk.Checkbutton(control_frame, text="Enable Joy Group", variable=self.joy_var, command=self.toggle_joy).pack()

        ## Leg gait dropdown
        self.gait_combo = ttk.Combobox(pi_frame, state='readonly', values=['ActionSteppy', 'BigSteppy', 'GoSteppy'])
        self.gait_combo.set('ActionSteppy')
        self.gait_combo.pack()

        ## SSH client dropdown
        self.ssh_combo = ttk.Combobox(root, state='readonly', values=['gabe@ros-24.local', 'gabe@ros-24', 'neil@nbrosbox'])
        self.ssh_combo.set('gabe@ros-24.local')
        self.ssh_combo.pack()

        ## Run & Stop buttons
        butt_frame = tk.Frame(root)
        butt_frame.pack(padx=PADX, pady=PADY, fill='both', expand=True)
        run_button = tk.Button(butt_frame, text='LAUNCH', bg='green', command=self.run_command).pack(side='left')
        stop_button = tk.Button(butt_frame, text='STOP ALL', bg='red', command=self.stop_command).pack(side='left')

    def toggle_sensor(self):
        if self.sensor_var.get():
            self.joy_var.set(False)

    def toggle_joy(self):
        if self.joy_var.get():
            self.sensor_var.set(False)
        
    def run_command(self):
        print('Launching:')
        pi_cmd = ['ros2', 'launch', 'spider_capstone_bringup',
                  'pi.launch.py']
        laptop_cmd = ['ros2', 'launch', 'spider_capstone_bringup',
                      'laptop.launch.py']

        ## Checkbutton states
        # Add to pi_cmd
        pi_cmd.append('core_group:=true' if self.core_var.get() else 'core_group:=false')
        pi_cmd.append('use_sensors:=true' if self.sensor_var.get() else 'use_sensors:=false')
        pi_cmd.append(f'gait_node:={self.gait_combo.get()}')

         # Add to laptop_cmd
        laptop_cmd.append('use_gui:=true' if self.gui_var.get() else 'use_gui:=false')
        laptop_cmd.append('use_joy:=true' if self.joy_var.get() else 'use_joy:=false')
    
        # Launch on local machine
        self.loc_proc = subprocess.Popen(laptop_cmd, preexec_fn=os.setsid)
        print(f'Local: {laptop_cmd = }')

        # Combine commands for remote ssh
        self.ssh_client = self.ssh_combo.get()
        pi_ssh = ["ssh", "-t", self.ssh_client]
        pi_source = "source /opt/ros/jazzy/setup.bash && source /home/gabe/ros2_ws/install/setup.bash"
        pi_cmd_str = shlex.join(pi_cmd)
        #pi_gait = f"ros2 run spider_capstone_trajectory {self.gait_combo.get()}"
        full_pi_cmd = [*pi_ssh, f"{pi_source} && {pi_cmd_str}"] # && {pi_gait}"]

        # Launch on remote Pi
        self.remote_proc = subprocess.Popen(full_pi_cmd)
        print(f'Remote: {full_pi_cmd = }')


    def stop_command(self):
        print('Stopping:')

        # Stop local process
        if self.loc_proc:
            #print(self.loc_proc)
            os.killpg(os.getpgid(self.loc_proc.pid), signal.SIGINT)
            print('Local process terminated')
            self.loc_proc = None

        # Stop remote process
        if self.remote_proc:
            kill_remote_cmd = ["ssh", self.ssh_client, "pkill -f 'ros2'"]
            subprocess.run(kill_remote_cmd)
            print('Remote process terminated')
            self.remote_proc = None
        
        print("All processes stopped!")

    def on_closing(self):
        self.stop_command()
        self.root.destroy()


def main():
    root = tk.Tk()
    gui = GuiLauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
