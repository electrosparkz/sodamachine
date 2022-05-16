import os
import time
import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from pprint import pprint

class FlavorButton(tk.Button):
    def __init__(self, parent, pump_index, flavor_info, grid_pos, callback, *args, **kwargs):
        self.base_dir = os.getcwd()
        self.parent = parent

        self.callback = callback

        self.pump_index = pump_index

        self.flavor = flavor_info

        self.flavor_name = self.flavor['name']
        self.flavor_icon = self.flavor['icon']
        self.flavor_size = self.flavor['size']

        self.grid_pos = grid_pos

        self.button_frame = tk.Frame(self.parent, bg=self.parent.cget('bg'))

        self.status_label = tk.Label(self.button_frame, bg="green", font=("Arial Bold", 10))

        self.photoimage = tk.PhotoImage(file=os.path.join(self.base_dir, "icons", self.flavor_icon))

        super().__init__(self.button_frame, image=self.photoimage, command=self.selected, *args, **kwargs)

        self.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        try:
            remaining_pct = round((self.parent.controller.state.syrup_remaining[self.pump_index] / (self.flavor_size * 4546)) * 100)
        except:
            remaining_pct = 0

        self.status_label.config(text=f"{self.flavor_size}g - Remain: {remaining_pct}%")

        self.status_label.grid(row=1, column=0, sticky="nsew", padx=3, pady=3)

        self.button_frame.grid(row=self.grid_pos[0], column=self.grid_pos[1], sticky="nsew", padx=10, pady=10)

    def selected(self):
        self.callback(self)


class ConfigureButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        


class FlavorInterfaceButtons(tk.Frame):
    def __init__(self, parent, flavor_name, pump_index, *args, **kwargs):
        self.parent = parent
        self.pump_index = pump_index

        self.flavor_name = flavor_name

        bottle_size = self.parent.controller.bottle_size

        if bottle_size not in ["large", "small"]:
            self.dose = 50
        else:
            self.dose = self.parent.controller.conf.flavors[self.pump_index]['pour'][bottle_size]

        self.init_dose = int(self.dose)

        self.steps_per_ml = self.parent.controller.conf.cal_values[self.pump_index]

        self.state = "idle"  # idle, dispense, done, stop

        super().__init__(self.parent, bg=self.parent.cget('bg'), *args, **kwargs)

        for x in range(5):
            self.columnconfigure(x, weight=1)
        for x in range(5):
            self.rowconfigure(x, weight=1)

        self.button_font = font.Font(family="Arial Bold", size=20)
        self.pbar_font = font.Font(family="Arial Bold", size=14)
        self.label_font = font.Font(family="Arial Bold", size=26)

        self.flavor_label = tk.Label(self.parent, text=self.flavor_name, fg="white", bg=self.parent.cget('bg'), font=self.label_font)
        self.flavor_label.place(anchor="n", relx=.5, rely=.04)

        self.back_button = tk.Button(self.parent,
                                     text="Back",
                                     bg="cyan",
                                     # height="20",
                                     # width="20",
                                     font=font.Font(family="Arial Bold", size=16),
                                     command=self.parent.controller.gui.display_flavor_picker)
        self.back_button.place(anchor="nw", height=40, width=70, x=15, y=15)


        self.dispense_button = tk.Button(self,
                                         text=f"Dispense\n\nAmount:\n{self.dose}ml", 
                                         command=self.dispense_pushed,
                                         bg="green",
                                         activebackground="green",
                                         font=self.button_font,
                                         width=1,
                                         height=1)

        self.dispense_button.grid(column=0, row=0, columnspan=3, rowspan=3, sticky="nsew", padx=10, pady=10)

        self.up_button_5 = tk.Button(self,
                                     text=f"+5ml",
                                     command=lambda: self.add_inc(5),
                                     bg="green",
                                     activebackground="green",
                                     font=self.button_font)
        self.up_button_10 = tk.Button(self,
                                      text=f"+10ml",
                                      command=lambda: self.add_inc(10),
                                      bg="green",
                                      activebackground="green",
                                      font=self.button_font)
        self.down_button_5 = tk.Button(self,
                                       text=f"-5ml",
                                       command=lambda: self.remove_inc(5),
                                       bg="red",
                                       activebackground="red",
                                       font=self.button_font)
        self.down_button_10 = tk.Button(self,
                                        text=f"-10ml",
                                        command=lambda: self.remove_inc(10),
                                        bg="red",
                                        activebackground="red",
                                        font=self.button_font)
        self.reset_button = tk.Button(self,
                                      text="RESET",
                                      command=self.reset_value,
                                      bg="yellow",
                                      activebackground="yellow",
                                      font=self.button_font)

        self.up_button_5.grid(row=0, column=3, sticky="nsew", padx=5, pady=10)
        self.up_button_10.grid(row=0, column=4, sticky="nsew", padx=5, pady=10)

        self.down_button_5.grid(row=2, column=3, sticky="nsew", padx=5, pady=10)
        self.down_button_10.grid(row=2, column=4, sticky="nsew", padx=5, pady=10)

        self.reset_button.grid(row=1, column=3, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.style = ttk.Style(self)
        self.style.layout("LabeledProgressbar",
            [('LabeledProgressbar.trough',
                {'children': [('LabeledProgressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'}),
                              ("LabeledProgressbar.label",   # label inside the bar
                              {"sticky": ""})],
                 'sticky': 'nswe'})])

        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate', style="LabeledProgressbar")
        self.style.configure("LabeledProgressbar",
                             text=f"Ready",
                             font=self.pbar_font,
                             background="green")
        self.progress_bar.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)

        self.place(anchor="c", relx=.5, rely=.55, relheight=.8, relwidth=.8)


    def _update_button_text(self):
        self.dispense_button.config(text=f"Dispense\n\nAmount:\n{self.dose}ml")

    def add_inc(self, val):
        self.dose += val
        self._update_button_text()

    def remove_inc(self, val):
        self.dose -= val
        self._update_button_text()

    def reset_value(self):
        self.dose = self.init_dose
        self._update_button_text()

    def dispense_pushed(self):
        if self.state == "idle":
            self.state = "dispense"
            self.dispense_button.config(bg="red", activebackground="red", text=f"Dispensing\n(Press to stop)\n\n")
            for button in [self.up_button_5,
                           self.up_button_10,
                           self.down_button_5,
                           self.down_button_10,
                           self.reset_button,
                           self.back_button]:
                button.config(state="disabled")
            self.style.configure("LabeledProgressbar",
                                 text=f"Priming",
                                 font=self.pbar_font,
                                 background="green")
            self.start_dispense()
        elif self.state == "dispense":
            self.state = "stop"

    def start_dispense(self):

        self.parent.controller.pc.pump_start(self.pump_index, "F", self.steps_per_ml, self.dose)
        self.dispense_started = round(time.time(), 2)
        self._dispense_loop()

    def _dispense_loop(self):
        try:
            if self.state == "dispense":
                # time_remaining = round(self.pump_runtime - (time.time() - self.dispense_started), 2)
                time_elapsed = round(time.time() - self.dispense_started, 2)

                pump_status, ml_dispensed, last_diff = self.parent.controller.pc.status

                self._update_syrup_remaining(last_diff)

                ml_remaining = self.dose - ml_dispensed
                pct_done = 100 - round((ml_remaining / self.dose) * 100)

                print(f"{time_elapsed}, ml: {ml_remaining}, pct: {pct_done}, dose: {self.dose}")

                if pump_status == 0x00:
                    self.state = "done"
                else:
                    self.style.configure("LabeledProgressbar",
                                         text=f"{self.dose - ml_remaining:.2f}/{self.dose}ml - {pct_done}%",
                                         font=self.pbar_font,
                                         background="green")
                    self.progress_bar['value'] = pct_done
                    self.after(300, self._dispense_loop)
            elif self.state == "stop":
                self.parent.controller.pc.pump_stop(self.pump_index)
                self.dispense_button.config(text="HALTED", state="disabled")
                self.style.configure("LabeledProgressbar", background="red")
                self.back_button.configure(state="normal")
                self.parent.controller.pc.pump_stop(self.pump_index)
            
            if self.state == "done":
                self.dispense_button.config(text="Done!", state="disabled", bg="green", activebackground="green")
                self.style.configure("LabeledProgressbar", text="Done!", font=self.pbar_font)
                self.progress_bar['value'] = 100
                self.back_button.configure(state="normal")
                self.parent.controller.pc.pump_stop(self.pump_index)
        except:
            self.parent.controller.pc.pump_stop(self.pump_index)
            raise

    def _update_syrup_remaining(self, ml_dispensed):
        print(f"Update syrup: {ml_dispensed}")
        syrup_remain = self.parent.controller.state.syrup_remaining[self.pump_index]
        self.parent.controller.state.syrup_remaining[self.pump_index] = syrup_remain - ml_dispensed
