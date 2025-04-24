import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import  ImageGrab

def initialize_grid(size, prob=0.5):
    return np.random.choice([0, 1], size=(size, size), p=[1 - prob, prob])

def get_block(grid, i, j, wraparound):
    n = grid.shape[0]
    if wraparound:
        return np.array([
            [grid[i % n, j % n], grid[i % n, (j + 1) % n]],
            [grid[(i + 1) % n, j % n], grid[(i + 1) % n, (j + 1) % n]]
        ])
    else:
        if i + 1 >= n or j + 1 >= n:
            return None
        return grid[i:i + 2, j:j + 2]

def set_block(grid, block, i, j, wraparound):
    n = grid.shape[0]
    if wraparound:
        grid[i % n, j % n] = block[0, 0]
        grid[i % n, (j + 1) % n] = block[0, 1]
        grid[(i + 1) % n, j % n] = block[1, 0]
        grid[(i + 1) % n, (j + 1) % n] = block[1, 1]
    else:
        if i + 1 < n and j + 1 < n:
            grid[i:i + 2, j:j + 2] = block

def apply_rules(grid, wraparound, generation_number):
    n = grid.shape[0]
    new_grid = grid.copy()
    offset = 0 if generation_number % 2 == 1 else 1

    for i in range(offset, n, 2):
        for j in range(offset, n, 2):
            block = get_block(grid, i, j, wraparound)
            if block is None:
                continue
            ones = np.sum(block)
            if ones == 2:
                continue
            block = 1 - block
            if ones == 3:
                block = np.rot90(block, 2)
            set_block(new_grid, block, i, j, wraparound)

    return new_grid

def compute_stability(new_grid, old_grid):
    unchanged = np.sum(new_grid == old_grid)
    total = new_grid.size
    return (unchanged / total) * 100

def calculate_alive_ratio(grid):
    return np.sum(grid) / grid.size

def calculate_variance(grid):
    return np.var(grid)

def count_clusters(grid):
    n = grid.shape[0]
    visited = np.zeros_like(grid, dtype=bool)
    count = 0
    for i in range(n):
        for j in range(n):
            if grid[i, j] == 1 and not visited[i, j]:
                count += 1
                stack = [(i, j)]
                while stack:
                    x, y = stack.pop()
                    if 0 <= x < n and 0 <= y < n and not visited[x, y] and grid[x, y] == 1:
                        visited[x, y] = True
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx != 0 or dy != 0:
                                    stack.append((x + dx, y + dy))
    return count


class AutomatonVisualizer:
    def __init__(self, grid, wraparound):
        self.grid = grid
        self.wraparound = wraparound
        self.generation = 1
        self.cell_size = 20
        self.n = grid.shape[0]

        self.window = tk.Tk()
        self.window.title("Block Automaton")
        self.window.geometry("1200x800")

        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_width = self.n * self.cell_size
        self.canvas_height = self.n * self.cell_size
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))

        self.info_label = tk.Label(self.window, text="", font=("Helvetica", 16))
        self.info_label.pack(pady=10)

        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack()

        self.zoom_in_button = tk.Button(self.button_frame, text="Zoom In", font=("Helvetica", 14), command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=10)

        self.zoom_out_button = tk.Button(self.button_frame, text="Zoom Out", font=("Helvetica", 14), command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(self.button_frame, text="Next Generation", font=("Helvetica", 14), command=self.next_generation)
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(self.button_frame, text="Save as PNG", font=("Helvetica", 14), command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(self.button_frame, text="Exit", font=("Helvetica", 14), command=self.window.destroy)
        self.exit_button.pack(side=tk.LEFT, padx=10)

        self.draw_grid()
        self.window.mainloop()

    def draw_grid(self):
        self.canvas.delete("all")
        scale_x = self.cell_size
        scale_y = self.cell_size
        self.canvas_width = self.n * self.cell_size
        self.canvas_height = self.n * self.cell_size
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))

        # Draw red grid
        for i in range(0, self.n - 1):
            for j in range(0, self.n - 1):
                x0 = j * scale_x
                y0 = i * scale_y
                x1 = x0 + 2 * scale_x
                y1 = y0 + 2 * scale_y
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", dash=(4, 2))

        # Draw blue grid
        for i in range(0, self.n + 1, 2):
            y = i * scale_y
            self.canvas.create_line(0, y, self.canvas_width, y, fill="blue", width=2)
        for j in range(0, self.n + 1, 2):
            x = j * scale_x
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="blue", width=2)

        # Draw cells after grids
        for i in range(self.n):
            for j in range(self.n):
                x0 = j * scale_x + scale_x * 0.25
                y0 = i * scale_y + scale_y * 0.25
                x1 = j * scale_x + scale_x * 0.75
                y1 = i * scale_y + scale_y * 0.75

                color = "black" if self.grid[i, j] == 1 else "white"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

        self.update_metrics()

    def update_metrics(self):
        alive_ratio = calculate_alive_ratio(self.grid)
        variance = calculate_variance(self.grid)
        clusters = count_clusters(self.grid)
        text = (f"Generation: {self.generation}\n"
                f"Alive Ratio: {alive_ratio:.3f}\n"
                f"Variance: {variance:.5f}\n"
                f"Clusters: {clusters}")
        self.info_label.config(text=text)

    def next_generation(self):
        new_grid = apply_rules(self.grid, self.wraparound, self.generation)
        self.grid = new_grid
        self.generation += 1
        self.draw_grid()

    def zoom_in(self):
        self.cell_size += 2
        self.draw_grid()

    def zoom_out(self):
        if self.cell_size > 4:
            self.cell_size -= 2
            self.draw_grid()

    def save_image(self):
        self.window.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        img = ImageGrab.grab().crop((x, y, x1, y1))
        filename = f"generation_{self.generation}.png"
        img.save(filename)
        print(f"Saved {filename}")

def main():
    setup_window = tk.Tk()
    setup_window.title("Setup Parameters")
    setup_window.attributes("-fullscreen", True)

    main_frame = tk.Frame(setup_window)
    main_frame.pack(pady=100)

    tk.Label(main_frame, text="Choose initial probability for 1s:", font=("Helvetica", 16)).pack(pady=5)
    prob_var = tk.StringVar(value="0.5")
    prob_menu = ttk.Combobox(main_frame, textvariable=prob_var, values=["0.25", "0.5", "0.75"], state="readonly", font=("Helvetica", 14))
    prob_menu.pack()

    tk.Label(main_frame, text="Enable wraparound?", font=("Helvetica", 16)).pack(pady=5)
    wrap_var = tk.StringVar(value="yes")
    wrap_menu = ttk.Combobox(main_frame, textvariable=wrap_var, values=["yes", "no"], state="readonly", font=("Helvetica", 14))
    wrap_menu.pack()

    def start_simulation():
        try:
            prob = float(prob_var.get())
            wraparound = wrap_var.get().lower() == "yes"
            setup_window.destroy()
            grid = initialize_grid(100, prob)
            AutomatonVisualizer(grid, wraparound)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(main_frame, text="Start Simulation", font=("Helvetica", 16), command=start_simulation).pack(pady=20)
    tk.Button(main_frame, text="Exit", font=("Helvetica", 16), command=setup_window.destroy).pack()

    setup_window.mainloop()

if __name__ == "__main__":
    main()