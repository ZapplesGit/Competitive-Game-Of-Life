import customtkinter as ctk
import tkinter as tk
import random
from patterns import patterns  # Import patterns from patterns.py


# Constants
pixel_size = 16

# Code to reset patterns.py on startup
default_patterns = """# patterns.py

patterns = {
    "Spaceship": [(3, 0), (0, 0), (4, 1), (4, 2), (0, 2), (4, 3), (3, 3), (2, 3), (1, 3)],
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "Pulsar": [(2, 0), (3, 0), (4, 0), (8, 0), (9, 0), (10, 0), (0, 2), (5, 2), (7, 2), (12, 2),
               (0, 3), (5, 3), (7, 3), (12, 3), (0, 4), (5, 4), (7, 4), (12, 4), (2, 5), (3, 5),
               (4, 5), (8, 5), (9, 5), (10, 5), (2, 7), (3, 7), (4, 7), (8, 7), (9, 7), (10, 7),
               (0, 8), (5, 8), (7, 8), (12, 8), (0, 9), (5, 9), (7, 9), (12, 9), (0, 10), (5, 10),
               (7, 10), (12, 10), (2, 12), (3, 12), (4, 12), (8, 12), (9, 12), (10, 12)],
    "Gosper Glider Gun": [(24, 0), (22, 1), (24, 1), (12, 2), (13, 2), (20, 2), (21, 2), (34, 2),
                          (35, 2), (11, 3), (15, 3), (20, 3), (21, 3), (34, 3), (35, 3), (0, 4),
                          (1, 4), (10, 4), (16, 4), (20, 4), (21, 4), (0, 5), (1, 5), (10, 5), (14, 5),
                          (16, 5), (17, 5), (22, 5), (24, 5), (10, 6), (16, 6), (24, 6), (11, 7), (15, 7),
                          (12, 8), (13, 8)],
    "Pentadecathlon": [(1, 0), (2, 0), (3, 0), (0, 1), (4, 1), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3),
                       (0, 4), (4, 4), (1, 5), (2, 5), (3, 5), (1, 6), (2, 6), (3, 6), (0, 7), (4, 7), (1, 8),
                       (2, 8), (3, 8)],
}
"""

with open("patterns.py", "w") as f:
    f.write(default_patterns)


class GameOfLife:
    def __init__(self, master, width, height, cell_size=pixel_size):
        self.previous_states = None
        self.master = master
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.selected_pattern = "Spaceship"  # Default pattern
        self.generation_count = 0
        self.current_theme = "Light"  # Track the current theme

        # Create the canvas
        self.canvas = tk.Canvas(master, width=width * cell_size, height=height * cell_size, bg="white")
        self.canvas.pack(pady=20)
        self.canvas.configure(width=width * cell_size, height=height * cell_size)

        self.live_cells = {}

        # Bind events to canvas
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<Button-3>", self.place_pattern)  # Right-click to place pattern
        self.master.bind("<space>", lambda event: self.start_stop())  # Space bar to start/stop

        self.running = False

        # Adding control buttons with CustomTkinter
        self.start_stop_button = ctk.CTkButton(master, text="Start/Stop", command=self.start_stop)
        self.start_stop_button.pack(side=ctk.LEFT, padx=50, pady=10)

        self.clear_button = ctk.CTkButton(master, text="Clear", command=self.clear_grid)
        self.clear_button.pack(side=ctk.LEFT, padx=10, pady=10)

        self.random_button = ctk.CTkButton(master, text="Randomize", command=self.randomize_grid)
        self.random_button.pack(side=ctk.LEFT, padx=10, pady=10)

        self.counter_frame = ctk.CTkFrame(master, width=220, height=30, fg_color="lightgray")
        self.counter_frame.pack_propagate(False)
        self.counter_frame.pack(side=ctk.LEFT, pady=10)

        self.live_counter = ctk.CTkLabel(self.counter_frame, text="Live Count: Blue: 0, Red: 0", text_color="black")
        self.live_counter.pack()

        self.speed_scale = ctk.CTkSlider(master, from_=1, to=1000, orientation=ctk.HORIZONTAL, number_of_steps=999)
        self.speed_scale.set(1000)
        self.speed_scale.pack(side=ctk.RIGHT, padx=50, pady=10)
        self.speed_scale_label = ctk.CTkLabel(master, text="Speed")
        self.speed_scale_label.pack(side=ctk.RIGHT, padx=10, pady=10)

        # Initialize grid
        self.initialize_grid()

        # Add a menu for pattern selection and settings
        self.menu_bar = tk.Menu(master, bg="white")  # Set initial menu bar color
        self.pattern_menu = tk.Menu(self.menu_bar, tearoff=0)
        for pattern_name in patterns.keys():
            self.pattern_menu.add_command(label=pattern_name, command=lambda p=pattern_name: self.select_pattern(p))
        self.menu_bar.add_cascade(label="Patterns", menu=self.pattern_menu)

        # Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.settings_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)

        self.save_pattern_button = ctk.CTkButton(master, text="Save Pattern", command=self.save_pattern)
        self.save_pattern_button.pack(side=ctk.LEFT, padx=10, pady=10)

        master.configure(menu=self.menu_bar)

        # Show the information screen on startup
        self.show_info_screen()

    # New function to save the current grid as a pattern
    def save_pattern(self):
        # Get the live cells in relative positions
        pattern_name = self.prompt_for_pattern_name()
        if not pattern_name:
            return  # User canceled the action

        relative_pattern = []
        for (x, y), color in self.live_cells.items():
            if color == "blue":  # Only saving blue cells
                relative_pattern.append((x, y))

        # Normalize the pattern to start from (0, 0)
        if relative_pattern:
            min_x = min(x for x, y in relative_pattern)
            min_y = min(y for x, y in relative_pattern)
            normalized_pattern = [(x - min_x, y - min_y) for x, y in relative_pattern]
        else:
            normalized_pattern = []

        # Try to append the new pattern to patterns.py
        pattern_saved = self.append_pattern_to_file(pattern_name, normalized_pattern)

        # Only update the patterns menu and in-memory dictionary if the pattern was successfully saved
        if pattern_saved:
            self.pattern_menu.add_command(label=pattern_name, command=lambda p=pattern_name: self.select_pattern(p))
            patterns[pattern_name] = normalized_pattern  # Add the pattern to the in-memory dictionary
        else:
            print(f"Pattern '{pattern_name}' was not added to the menu or dictionary due to an error.")

    # Prompt user for pattern name
    def prompt_for_pattern_name(self):
        pattern_name_popup = tk.Toplevel(self.master)
        pattern_name_popup.title("Save Pattern")
        pattern_name_popup.geometry("300x225")

        label = ctk.CTkLabel(pattern_name_popup, text="Enter pattern name:")
        label.pack(pady=10)
        entry = ctk.CTkEntry(pattern_name_popup)
        entry.pack(pady=10)
        pattern_name = tk.StringVar()

        def on_submit():
            pattern_name.set(entry.get())
            pattern_name_popup.destroy()

        submit_button = ctk.CTkButton(pattern_name_popup, text="Submit", command=on_submit)
        submit_button.pack(pady=10)

        pattern_name_popup.wait_window()  # Wait for the window to close

        return pattern_name.get().strip()

    # Function to append the pattern to patterns.py
    def append_pattern_to_file(self, pattern_name, pattern_data):
        patterns_file = 'patterns.py'

        # Introduce a success flag
        is_valid = True

        # Ensure the pattern name is valid
        if not pattern_name.isidentifier():
            print("Pattern name is invalid, stopping.")
            self.show_error_popup("Invalid pattern name", "Pattern names must not contain special characters.")
            is_valid = False  # Set flag to False if the name is invalid

        # Read the file
        with open(patterns_file, 'r') as file:
            content = file.readlines()

        # Check if pattern name already exists in the file to prevent duplicates
        if any(f"'{pattern_name}':" in line for line in content):
            print("Pattern already exists, stopping.")
            self.show_error_popup("Pattern name exists", "A pattern with this name already exists.")
            is_valid = False  # Set flag to False if the pattern already exists

        # Only append and write to the file if is_valid is still True
        if is_valid:
            # Prepare the pattern string
            pattern_str = f"    '{pattern_name}': {pattern_data},\n"

            # Find where to insert the new pattern (before the closing brace)
            for i in range(len(content)-1, -1, -1):
                if content[i].strip() == "}":
                    content.insert(i, pattern_str)
                    break

            # Write the file back with the new pattern
            with open(patterns_file, 'w') as file:
                file.writelines(content)

            print(f"Pattern '{pattern_name}' saved to patterns.py.")
            return True  # Return True to indicate successful saving
        else:
            print(f"Pattern '{pattern_name}' was not saved due to an error.")
            return False  # Return False to indicate failure

    # Function to show an error pop-up window
    def show_error_popup(self, title, message):
        error_popup = tk.Toplevel(self.master)
        error_popup.title(title)
        error_popup.geometry("300x150")

        label = ctk.CTkLabel(error_popup, text=message, wraplength=250)
        label.pack(pady=20)

        close_button = ctk.CTkButton(error_popup, text="OK", command=error_popup.destroy)
        close_button.pack(pady=10)

        # Ensure the user interacts with this window first
        error_popup.lift(self.master)
        error_popup.focus_set()
        error_popup.grab_set()

    # Toggle theme between Light and Dark
    def toggle_theme(self):
        if self.current_theme == "Light":
            ctk.set_appearance_mode("Dark")
            self.current_theme = "Dark"
            self.canvas.configure(bg="lightgray")  # Set the grid background to gray
            self.menu_bar.configure(bg="black", fg="black")  # Set the menu background to black
            self.counter_frame.configure(fg_color="black")  # Set the counter frame background to black
            self.live_counter.configure(text_color="white")  # Set the text color to white
        else:
            ctk.set_appearance_mode("Light")
            self.current_theme = "Light"
            self.canvas.configure(bg="white")  # Set the grid background to white
            self.menu_bar.configure(bg="white", fg="black")  # Set the menu background to white
            self.counter_frame.configure(fg_color="lightgray")  # Set the counter frame background to white
            self.live_counter.configure(text_color="black")  # Set the text color to black

        self.draw_grid()

    def show_info_screen(self):
        info_screen = tk.Toplevel(self.master)
        info_screen.title("Welcome to Competitive Game of Life")
        info_screen.geometry("530x450")
        info_screen.resizable(False, False)

        # Center the info screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (450 / 2))
        y_coordinate = int((screen_height / 2) - (350 / 2))
        info_screen.geometry(f"+{x_coordinate}+{y_coordinate}")

        instructions = """
Welcome to the Competitive Game of Life!

How to play:
- Left-click: Toggle a cell's state.
- Drag left-click: Paint cells.
- Right-click: Place a selected pattern.
- Space bar: Start/Stop the simulation.

Objective:
- Compete to dominate the board with your color.
- The game ends when a stable state is reached or an infinite loop is detected.

Good luck!
        """

        label = ctk.CTkLabel(info_screen, text=instructions, text_color="black", wraplength=420)
        label.pack(expand=True, padx=20, pady=20)

        close_button = ctk.CTkButton(info_screen, text="Start", command=info_screen.destroy)
        close_button.pack(pady=10)

        info_screen.lift(self.master)  # Bring the info screen to the front
        info_screen.focus_set()  # Ensure the info screen receives focus
        info_screen.grab_set()  # Ensure the user interacts with this window first

    def initialize_grid(self):
        self.live_cells = {}
        half_width = self.width // 2
        blue_cells = set()
        red_cells = set()
        for y in range(self.height):
            for x in range(self.width):
                if x < half_width:
                    if random.choice([0, 1]) == 1:
                        blue_cells.add((x, y))
                else:
                    if random.choice([0, 1]) == 1:
                        red_cells.add((x, y))

        # Balance the number of cells when randomized
        while len(blue_cells) > len(red_cells):
            blue_cells.pop()
        while len(red_cells) > len(blue_cells):
            red_cells.pop()

        for x, y in blue_cells:
            self.live_cells[(x, y)] = "blue"
        for x, y in red_cells:
            self.live_cells[(x, y)] = "red"

        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.generation_count = 0
        self.draw_grid()
        self.update_live_counter()

    def hash_grid(self):
        return frozenset(self.live_cells.items())

    def draw_grid(self):
        self.canvas.delete("all")

        # Set grid line color based on the current theme
        grid_line_color = "lightgray" if self.current_theme == "Light" else "gray"

        # Draw cells
        for (x, y), color in self.live_cells.items():
            # Check if the color is red, and modify it for dark mode
            if color == "red" and self.current_theme == "Dark":
                color = "#ED0000"  # Use darker red in dark mode

            self.canvas.create_rectangle(
                x * self.cell_size, y * self.cell_size,
                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                fill=color, outline="gray"
            )

        # Draw grid lines
        for x in range(0, self.width * self.cell_size, self.cell_size):
            self.canvas.create_line(x, 0, x, self.height * self.cell_size, fill=grid_line_color)
        for y in range(0, self.height * self.cell_size, self.cell_size):
            self.canvas.create_line(0, y, self.width * self.cell_size, y, fill=grid_line_color)

        # Draw the middle line when the simulation is not running
        if not self.running:
            middle_x = (self.width // 2) * self.cell_size
            self.canvas.create_line(
                middle_x, 0, middle_x, self.height * self.cell_size,
                fill="black", width=2  # Thicker black line
            )

    def update(self):  # Updates the grid according the Game of Life rules
        new_live_cells = {}
        neighbor_counts = {}

        for (x, y) in self.live_cells:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = (x + dx) % self.width, (y + dy) % self.height
                    if (nx, ny) not in neighbor_counts:
                        neighbor_counts[(nx, ny)] = {"count": 0, "blue": 0, "red": 0}  # Sets the cell count
                    neighbor_counts[(nx, ny)]["count"] += 1
                    if self.live_cells.get((x, y)) == "blue":
                        neighbor_counts[(nx, ny)]["blue"] += 1  # Adds to the blue count
                    elif self.live_cells.get((x, y)) == "red":
                        neighbor_counts[(nx, ny)]["red"] += 1  # Adds to the red count

        for (cell, data) in neighbor_counts.items():  # Counts the number of neighbours
            if data["count"] == 3 or (data["count"] == 2 and cell in self.live_cells):
                if data["blue"] > data["red"]:
                    new_live_cells[cell] = "blue"  # Turns the cell blue
                elif data["red"] > data["blue"]:
                    new_live_cells[cell] = "red"  # Turns the cell red
            else:
                new_live_cells[cell] = None  # Cell dies

        # Check if the new state is a recurrence or if nothing changed
        new_state_hash = frozenset((cell, color) for cell, color in new_live_cells.items() if color is not None)
        if new_state_hash in self.previous_states:
            self.running = False
            print("Infinite loop detected. Simulation stopped.")
            self.display_winner()
            return

        if new_state_hash == self.hash_grid():
            self.running = False
            print("No changes detected. Simulation stopped.")
            self.display_winner()
            return

        self.live_cells = {cell: color for cell, color in new_live_cells.items() if color is not None}
        self.previous_states.add(new_state_hash)
        self.generation_count += 1
        self.draw_grid()
        self.update_live_counter()

        inverted_speed = int(1001 - self.speed_scale.get())  # Inverts the speed slider

        if self.running:
            self.master.after(inverted_speed, self.update)

    def update_live_counter(self):
        blue_count = sum(1 for color in self.live_cells.values() if color == "blue")
        red_count = sum(1 for color in self.live_cells.values() if color == "red")
        self.live_counter.configure(text=f"Live Count: Blue: {blue_count}, Red: {red_count}")

        # Check if either team has zero cells

        if blue_count == 0 or red_count == 0:
            if self.generation_count <= 1:
                return
            self.running = False
            self.display_winner()

    # Displays the winner in console and calls the splash screen if conditions are met
    def display_winner(self):
        if self.generation_count <= 1:
            return

        blue_count = sum(1 for color in self.live_cells.values() if color == "blue")
        red_count = sum(1 for color in self.live_cells.values() if color == "red")

        # Determine the winner
        if blue_count == 0:
            winner = "Red wins!"
        elif red_count == 0:
            winner = "Blue wins!"
        elif blue_count > red_count:
            winner = "Blue wins!"
        elif red_count > blue_count:
            winner = "Red wins!"
        else:
            winner = "It's a tie!"

        print(f"Blue: {blue_count}, Red: {red_count}. {winner}")
        self.show_winner_splash(winner)

    # Shows the splash screen with the winner announcement
    def show_winner_splash(self, winner_message):
        splash = tk.Toplevel(self.master)
        splash.title("Winner Announcement")
        splash.geometry("300x200")
        splash.resizable(False, False)

        # Center the splash screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (300 / 2))
        y_coordinate = int((screen_height / 2) - (200 / 2))
        splash.geometry(f"+{x_coordinate}+{y_coordinate}")

        message = ctk.CTkLabel(splash, text=winner_message, text_color="black")
        message.pack(expand=True)

        # Modified 'OK' button to show the info screen after closing the splash
        ok_button = ctk.CTkButton(splash, text="OK", command=lambda: [splash.destroy(), self.show_info_screen()])
        ok_button.pack(pady=10)

        splash.grab_set()  # Ensure the user interacts with this window first

    def start_stop(self):
        self.running = not self.running
        if self.running:
            self.update()

    def clear_grid(self):
        self.running = False
        self.live_cells = {}
        self.previous_states = set()
        self.generation_count = 0
        self.draw_grid()
        self.update_live_counter()

    def randomize_grid(self):
        self.initialize_grid()

    def toggle_cell(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if (x, y) in self.live_cells:
            del self.live_cells[(x, y)]
        else:
            self.live_cells[(x, y)] = "blue" if x < self.width // 2 else "red"
        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.generation_count = 0
        self.draw_grid()
        self.update_live_counter()

    def paint_cell(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        self.live_cells[(x, y)] = "blue" if x < self.width // 2 else "red"
        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.generation_count = 0
        self.draw_grid()
        self.update_live_counter()

    def place_pattern(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        pattern = patterns[self.selected_pattern]

        # Check if the pattern should be inverted (on the right-hand side)
        half_width = self.width // 2
        if x >= half_width:
            max_x = max(dx for dx, dy in pattern)
            inverted_pattern = [(max_x - dx, dy) for dx, dy in pattern]
            pattern = inverted_pattern

        for dx, dy in pattern:
            new_x, new_y = (x + dx) % self.width, (y + dy) % self.height
            self.live_cells[(new_x, new_y)] = "blue" if x < self.width // 2 else "red"

        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.generation_count = 0
        self.draw_grid()
        self.update_live_counter()

    def select_pattern(self, pattern_name):
        self.selected_pattern = pattern_name


def main():
    ctk.set_appearance_mode("Light")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    root = ctk.CTk()
    root.title("Competitive Game of Life")

    # Option to toggle fullscreen mode using F11
    root.bind("<F11>", lambda event: root.attributes("-fullscreen", not root.attributes("-fullscreen")))

    root.after(0, lambda: root.state('zoomed'))

    GameOfLife(root, width=96, height=54)
    root.mainloop()


main()
