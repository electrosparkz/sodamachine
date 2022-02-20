import os
import time
import tkinter as tk
from tkinter import ttk

from config import SodaConfig
from buttons import FlavorButton, FlavorInterfaceButtons


class SodaGui(tk.Tk):
    def __init__(self, controller, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.controller = controller

        self.title("soda test")
        self.geometry("800x480")

        if os.name != 'nt':
            self.attributes('-fullscreen',True)
            self.config(cursor="none")

        self.main_container = tk.Frame(self, height=430, width=790, bg="blue")
        self.main_container.place(x=5, y=5)

        self.status_container = tk.Frame(self, height=35, width=790, bg="green")
        self.status_container.place(x=5, y=440)

        self.time_widget = TimeWidget(self.status_container, self.controller)
        self.temp_widget = TempWidget(self.status_container, self.controller)

        self.current_main_widget = None

        # self.display_flavor_picker()

    def display_flavor_picker(self):
        if self.current_main_widget:
            self.current_main_widget.destroy()
        self.current_main_widget = FlavorPicker(self.main_container, self.controller)

    def display_picked_flavor(self, flavor_button):
        if self.current_main_widget:
            self.current_main_widget.destroy()
        self.current_main_widget = FlavorInterface(self.main_container, self.controller, flavor_button) 

    def display_bottle_inserted(self):
        pass

    def display_goodbye(self):
        pass

    def display_idle_screen(self):
        if self.current_main_widget:
            self.current_main_widget.destroy()
        self.current_main_widget = IdleScreen(self.main_container, self.controller)


class IdleFlavorStatusWidget(tk.Label):
    def __init__(self, parent, controller, grid_pos, index, *args, **kwargs):
        self.parent = parent
        self.controller = controller
        self.index = index
        self.grid_pos = grid_pos

        flavor_size = self.controller.conf.flavors[index]['size']
        flavor_name = self.controller.conf.flavors[index]['name']

        if flavor_size != 0:
            percent_remaining = round((self.controller.state.syrup_remaining[index] / (flavor_size * 4546)) * 100)
        else:
            percent_remaining = 0

        super().__init__(self.parent, *args, **kwargs)

        self.config(text=f"{flavor_name}\nSyrup size: {flavor_size}gal\nSyrup Remaining: {percent_remaining}%")

        self.grid(row=self.grid_pos[0], column=self.grid_pos[1], sticky="nsew", padx=5, pady=5)


class IdleScreen(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.controller = controller

        self.config(bg=self.parent.cget('bg'))

        self.grid_width = 2

        grid_x = grid_y = 0

        for index, flavor in enumerate(self.controller.conf.flavors):
            flavor_widget = IdleFlavorStatusWidget(self, self.controller, (grid_x, grid_y), index)
            grid_y += 1
            if (grid_y == self.grid_width):
                grid_x += 1
                grid_y = 0

        self.place(anchor="c", relx=.5, rely=.5)


class FlavorInterface(tk.Frame):
    def __init__(self, parent, controller, flavor_button, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.controller = controller

        self.pump_index = int(flavor_button.pump_index)
        self.flavor_name = str(flavor_button.flavor_name)
        self.flavor_size = int(flavor_button.flavor_size)

        flavor_button.destroy()

        self.parent = parent

        self.config(bg=self.parent.cget('bg'))

        self.buttons = FlavorInterfaceButtons(self, self.flavor_name, self.pump_index)

        # self.place(height=100, width=100)
        self.place(anchor="c", relx=.5, rely=.5, relheight=1, relwidth=1)


class FlavorPicker(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.controller = controller

        self.grid_width = 4

        self.parent = parent

        self.buttons = []

        self.config(bg=self.parent.cget('bg'))

        grid_x = grid_y = 0
        for index, flavor in enumerate(self.controller.conf.flavors):
            flavor_button = FlavorButton(self,
                index,
                flavor,
                (grid_x, grid_y),
                self.picked_flavor,
                bg=self.parent.cget('bg'))
            self.buttons.append(flavor_button)
            grid_y += 1
            if (grid_y == self.grid_width):
                grid_x = 1
                grid_y = 0

        self.place(anchor="c", relx=.5, rely=.5)

    def picked_flavor(self, button):
        self.controller.gui.display_picked_flavor(button)


class TimeWidget(tk.Label):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.controller = controller

        self.config(bg=self.parent.cget('bg'))
        self.config(font=("Arial Bold", 18))

        self.place(anchor="w", relx=0, rely=.5)

        self.tick()

    def tick(self):
        self.config(text=time.ctime())
        self.after(300, self.tick)


class TempWidget(tk.Label):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.controller = controller

        self.config(bg=self.parent.cget('bg'))
        self.config(font=("Arial Bold", 18))

        # self.grid(row=0, column=1, sticky="e")
        self.place(anchor="e", relx=1, rely=.5)

        self.tick()

    def tick(self):
        self.controller.sensors.update_temp()
        self.config(text=f"{round(self.controller.sensors.temp, 2)}°F")
        self.after(1000, self.tick)


def main():
    config = SodaConfig()
    gui_app = SodaGui(config)
    gui_app.mainloop()

if __name__ == '__main__':
    main()
