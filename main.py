import tkinter as tk
import random

class GameOfLife:
    def __init__(self, master, width, height, cell_size=10):
        self.master = master
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.canvas = tk.Canvas(master, width=width * cell_size, height=height * cell_size)
        self.canvas.pack()
        self.live_cells = {}
        self.purple_life_count = {}  # To track consecutive generations of purple cells
        self.previous_states = set()
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.canvas.bind("<Button-3>", self.place_glider)  # Right-click to place glider
        self.running = False

        # Initialize grid with balanced blue on the left and red on the right
        self.initialize_grid()

        # Adding control buttons
        self.start_stop_button = tk.Button(master, text="Start/Stop", command=self.start_stop)
        self.start_stop_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(master, text="Clear", command=self.clear_grid)
        self.clear_button.pack(side=tk.LEFT)

        self.random_button = tk.Button(master, text="Randomize", command=self.randomize_grid)
        self.random_button.pack(side=tk.LEFT)

        self.speed_scale = tk.Scale(master, from_=1, to=1000, orient=tk.HORIZONTAL, label="Speed")
        self.speed_scale.set(1000)
        self.speed_scale.pack(side=tk.RIGHT)

        self.bot_scale = tk.Scale(master, from_=1, to=100, orient=tk.HORIZONTAL, label="Purple spreading")
        self.bot_scale.set(3)
        self.bot_scale.pack(side=tk.RIGHT)

    def initialize_grid(self):
        self.live_cells = {}
        self.purple_life_count = {}
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

        # Balance the number of cells if needed
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
                        neighbor_counts[(nx, ny)] = {"count": 0, "blue": 0, "red": 0, "purple": 0}
                    neighbor_counts[(nx, ny)]["count"] += 1
                    if self.live_cells[(x, y)] == "blue":
                        neighbor_counts[(nx, ny)]["blue"] += 1
                    elif self.live_cells[(x, y)] == "red":
                        neighbor_counts[(nx, ny)]["red"] += 1
                    else:  # purple cell
                        neighbor_counts[(nx, ny)]["purple"] += 1

        for (cell, data) in neighbor_counts.items():
            if data["count"] == 3 or (data["count"] == 2 and cell in self.live_cells):
                if data["blue"] > data["red"] and data["blue"] > data["purple"]:
                    new_live_cells[cell] = "blue"
                elif data["red"] > data["blue"] and data["red"] > data["purple"]:
                    new_live_cells[cell] = "red"
                elif data["purple"] > data["blue"] and data["purple"] > data["red"]:
                    new_live_cells[cell] = "purple"
                else:
                    new_live_cells[cell] = "purple"  # Default to purple in case of a tie

        # Update purple life count and remove purple cells that have been purple for certain num of generations
        for cell in list(new_live_cells):
            if new_live_cells[cell] == "purple":
                if cell in self.purple_life_count:
                    self.purple_life_count[cell] += 1
                    if self.purple_life_count[cell] >= self.bot_scale.get():
                        del new_live_cells[cell]
                        del self.purple_life_count[cell]
                else:
                    self.purple_life_count[cell] = 1
            elif cell in self.purple_life_count:
                del self.purple_life_count[cell]

        # Check if the new state is a recurrence or if nothing changed
        new_state_hash = frozenset(new_live_cells.items())
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

        self.live_cells = new_live_cells
        self.previous_states.add(new_state_hash)
        self.draw_grid()

        inverted_speed = 1001 - self.speed_scale.get()

        if self.running:
            self.master.after(inverted_speed, self.update)

    def display_winner(self):
        blue_count = sum(1 for color in self.live_cells.values() if color == "blue")
        red_count = sum(1 for color in self.live_cells.values() if color == "red")
        purple_count = sum(1 for color in self.live_cells.values() if color == "purple")
        if blue_count > red_count and blue_count > purple_count:
            winner = "Blue wins!"
        elif red_count > blue_count and red_count > purple_count:
            winner = "Red wins!"
        elif purple_count > blue_count and purple_count > red_count:
            winner = "purple wins!"
        else:
            winner = "It's a tie!"
        print(f"Blue: {blue_count}, Red: {red_count}, purple: {purple_count}. {winner}")

    def start_stop(self):
        self.running = not self.running
        if self.running:
            self.update()

    def clear_grid(self):
        self.running = False
        self.live_cells = {}
        self.purple_life_count = {}
        self.previous_states = set()
        self.draw_grid()

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

    def place_glider(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size

        glider_pattern = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)] if x < self.width // 2 else [(2, 1), (1, 2), (0, 0), (0, 1), (0, 2)]


        for dx, dy in glider_pattern:
            new_x, new_y = (x + dx) % self.width, (y + dy) % self.height
            self.live_cells[(new_x, new_y)] = "blue" if x < self.width // 2 else "red"

        self.previous_states = set()
        self.previous_states.add(self.hash_grid())
        self.draw_grid()

def main():
    root = tk.Tk()
    root.title("Conway's Game of Life")
    game = GameOfLife(root, width=96, height=54)
    root.mainloop()

if __name__ == "__main__":
    main()
