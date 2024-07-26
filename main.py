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
        self.grid = [[random.choice([0, 1]) for _ in range(width)] for _ in range(height)]
        self.draw_grid()
        self.running = False

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

    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(self.height):
            for x in range(self.width):
                color = "black" if self.grid[y][x] == 1 else "white"
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=color, outline="gray"
                )

    def update(self):
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                live_neighbors = sum(
                    self.grid[(y + dy) % self.height][(x + dx) % self.width]
                    for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx != 0 or dy != 0)
                )
                if self.grid[y][x] == 1:
                    if live_neighbors < 2 or live_neighbors > 3:
                        new_grid[y][x] = 0
                    else:
                        new_grid[y][x] = 1
                else:
                    if live_neighbors == 3:
                        new_grid[y][x] = 1
        self.grid = new_grid
        self.draw_grid()
        if self.running:
            self.master.after(self.speed_scale.get(), self.update)

    def start_stop(self):
        self.running = not self.running
        if self.running:
            self.update()

    def clear_grid(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.draw_grid()

    def randomize_grid(self):
        self.grid = [[random.choice([0, 1]) for _ in range(self.width)] for _ in range(self.height)]
        self.draw_grid()

def main():
    root = tk.Tk()
    root.title("Conway's Game of Life")
    game = GameOfLife(root, width=100, height=60)
    root.mainloop()

if __name__ == "__main__":
    main()
