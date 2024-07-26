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
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.running = False

        # Initialize grid with blue on the left and red on the right
        self.initialize_grid()

        # Adding control buttons
        self.start_stop_button = tk.Button(master, text="Start/Stop", command=self.start_stop)
        self.start_stop_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(master, text="Clear", command=self.clear_grid)
        self.clear_button.pack(side=tk.LEFT)

        self.random_button = tk.Button(master, text="Randomize", command=self.randomize_grid)
        self.random_button.pack(side=tk.LEFT)

        self.speed_scale = tk.Scale(master, from_=10, to=1000, orient=tk.HORIZONTAL, label="Speed (ms)")
        self.speed_scale.set(100)
        self.speed_scale.pack(side=tk.RIGHT)

    def initialize_grid(self):
        self.live_cells = {}
        for y in range(self.height):
            for x in range(self.width):
                if x < self.width // 2:
                    if random.choice([0, 1]) == 1:
                        self.live_cells[(x, y)] = "blue"
                else:
                    if random.choice([0, 1]) == 1:
                        self.live_cells[(x, y)] = "red"
        self.draw_grid()

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
                    if self.live_cells[(x, y)] == "blue":
                        neighbor_counts[(nx, ny)]["blue"] += 1
                    else:
                        neighbor_counts[(nx, ny)]["red"] += 1

        for (cell, data) in neighbor_counts.items():
            if data["count"] == 3 or (data["count"] == 2 and cell in self.live_cells):
                if data["blue"] > data["red"]:
                    new_live_cells[cell] = "blue"
                else:
                    new_live_cells[cell] = "red"

        self.live_cells = new_live_cells
        self.draw_grid()
        if self.running:
            self.master.after(self.speed_scale.get(), self.update)

    def start_stop(self):
        self.running = not self.running
        if self.running:
            self.update()

    def clear_grid(self):
        self.running = False
        self.live_cells = {}
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
        self.draw_grid()

def main():
    root = tk.Tk()
    root.title("Conway's Game of Life")
    game = GameOfLife(root, width=100, height=60)
    root.mainloop()

if __name__ == "__main__":
    main()
