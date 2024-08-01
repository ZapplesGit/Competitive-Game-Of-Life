import customtkinter as ctk
import tkinter as tk
import random
from patterns import patterns  # Import patterns from patterns.py


class GameOfLife:
    def __init__(self, master, width, height, cell_size=10):
        self.master = master
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.selected_pattern = "Glider"  # Default pattern

        # Create the canvas
        self.canvas = tk.Canvas(master, width=width * cell_size, height=height * cell_size)
        self.canvas.pack(pady=20)

        self.live_cells = {}

        # Bind events to canvas
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<Button-3>", self.place_pattern)  # Right-click to place pattern

        self.running = False

        # Adding control buttons with CustomTkinter
        self.start_stop_button = ctk.CTkButton(master, text="Start/Stop", command=self.start_stop)
        self.start_stop_button.pack(side=ctk.LEFT, padx=10, pady=10)

        self.clear_button = ctk.CTkButton(master, text="Clear", command=self.clear_grid)
        self.clear_button.pack(side=ctk.LEFT, padx=10, pady=10)

        self.random_button = ctk.CTkButton(master, text="Randomize", command=self.randomize_grid)
        self.random_button.pack(side=ctk.LEFT, padx=10, pady=10)

        self.speed_scale = ctk.CTkSlider(master, from_=1, to=1000, orientation=ctk.HORIZONTAL, number_of_steps=999)
        self.speed_scale.set(1000)
        self.speed_scale.pack(side=ctk.RIGHT, padx=10, pady=10)
        self.speed_scale_label = ctk.CTkLabel(master, text="Speed")
        self.speed_scale_label.pack(side=ctk.RIGHT, padx=10, pady=10)

        # Initialize live counter
        self.live_counter = ctk.CTkLabel(master, text="Live Count: Blue: 0, Red: 0", text_color="black")
        self.live_counter.pack(side=ctk.BOTTOM, pady=10)

        # Initialize grid
        self.initialize_grid()

        # Add a menu for pattern selection
        self.menu_bar = tk.Menu(master)
        self.pattern_menu = tk.Menu(self.menu_bar, tearoff=0)
        for pattern_name in patterns.keys():
            self.pattern_menu.add_command(label=pattern_name, command=lambda p=pattern_name: self.select_pattern(p))
        self.menu_bar.add_cascade(label="Patterns", menu=self.pattern_menu)
        master.config(menu=self.menu_bar)

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
        self.draw_grid()
        self.update_live_counter()

    def hash_grid(self):
        return frozenset(self.live_cells.items())

    def draw_grid(self):
        self.canvas.delete("all")
        # Draw cells
        for (x, y), color in self.live_cells.items():
            self.canvas.create_rectangle(
                x * self.cell_size, y * self.cell_size,
                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                fill=color, outline="gray"
            )
        # Draw grid lines
        for x in range(0, self.width * self.cell_size, self.cell_size):
            self.canvas.create_line(x, 0, x, self.height * self.cell_size, fill="lightgray")
        for y in range(0, self.height * self.cell_size, self.cell_size):
            self.canvas.create_line(0, y, self.width * self.cell_size, y, fill="lightgray")

    def update(self):
        new_live_cells = {}
        neighbor_counts = {}

        for (x, y) in self.live_cells:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = (x + dx) % self.width, (y + dy) % self.height
                    if (nx, ny) not in neighbor_counts:
                        neighbor_counts[(nx, ny)] = {"count": 0, "blue": 0, "red": 0}
                    neighbor_counts[(nx, ny)]["count"] += 1
                    if self.live_cells.get((x, y)) == "blue":
                        neighbor_counts[(nx, ny)]["blue"] += 1
                    elif self.live_cells.get((x, y)) == "red":
                        neighbor_counts[(nx, ny)]["red"] += 1

        for (cell, data) in neighbor_counts.items():
            if data["count"] == 3 or (data["count"] == 2 and cell in self.live_cells):
                if data["blue"] > data["red"]:
                    new_live_cells[cell] = "blue"
                elif data["red"] > data["blue"]:
                    new_live_cells[cell] = "red"
                else:
                    new_live_cells[cell] = self.live_cells.get(cell, "blue")  # Default to existing color
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
        self.draw_grid()
        self.update_live_counter()

        inverted_speed = int(1001 - self.speed_scale.get())  # Inverts the speed slider

        if self.running:
            self.master.after(inverted_speed, self.update)

    def update_live_counter(self):
        blue_count = sum(1 for color in self.live_cells.values() if color == "blue")
        red_count = sum(1 for color in self.live_cells.values() if color == "red")
        self.live_counter.configure(text=f"Live Count: Blue: {blue_count}, Red: {red_count}")

    # Displays the winner in console
    def display_winner(self):
        blue_count = sum(1 for color in self.live_cells.values() if color == "blue")
        red_count = sum(1 for color in self.live_cells.values() if color == "red")
        if blue_count > red_count:
            winner = "Blue wins!"
        elif red_count > blue_count:
            winner = "Red wins!"
        else:
            winner = "It's a tie!"
        print(f"Blue: {blue_count}, Red: {red_count}. {winner}")

    def start_stop(self):
        self.running = not self.running
        if self.running:
            self.update()

    def clear_grid(self):
        self.running = False
        self.live_cells = {}
        self.previous_states = set()
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
        self.draw_grid()
        self.update_live_counter()

    def paint_cell(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        self.live_cells[(x, y)] = "blue" if x < self.width // 2 else "red"
        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.draw_grid()
        self.update_live_counter()

    def place_pattern(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        pattern = patterns[self.selected_pattern]

        for dx, dy in pattern:
            new_x, new_y = (x + dx) % self.width, (y + dy) % self.height
            self.live_cells[(new_x, new_y)] = "blue" if x < self.width // 2 else "red"

        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.draw_grid()
        self.update_live_counter()

    def select_pattern(self, pattern_name):
        self.selected_pattern = pattern_name


def main():
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    root = ctk.CTk()
    root.title("Competitive Game of Life")
    game = GameOfLife(root, width=96, height=54)  # Size of grid
    root.mainloop()


main()
