import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab

# === Core Functions ===

def initialize_random_grid(size, prob=0.5):
    return np.random.choice([0, 1], size=(size, size), p=[1 - prob, prob])

# Support multiple starting patterns
def initialize_grid(size, prob=0.5, mode='random'):
    grid = np.zeros((size, size), dtype=int)

    if mode == 'random':
        grid = np.random.choice([0, 1], size=(size, size), p=[1 - prob, prob])

    elif mode == 'sparse':
        for _ in range(5):
            x = np.random.randint(0, size - 6)
            y = np.random.randint(0, size - 6)
            block = np.random.choice([0, 1], size=(6, 6), p=[0.7, 0.3])
            grid[x:x+6, y:y+6] = block

    elif mode == 'glider':
        def insert_glider(g, top_left_x, top_left_y):
            glider = np.array([
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 1]
            ])
            g[top_left_x:top_left_x+3, top_left_y:top_left_y+3] = glider

        insert_glider(grid, 1, 1)
        insert_glider(grid, size//2, size//2)
        insert_glider(grid, size//4, size//4)
        insert_glider(grid, (3*size)//4, (3*size)//4)

    elif mode == 'blinker':
        mid = size // 2
        grid[mid, mid-1:mid+2] = 1

    elif mode == 'oscillator':
        mid = size // 2
        grid[mid-1:mid+2, mid-1] = 1
        grid[mid+1, mid] = 1
        grid[mid-1, mid+1] = 1

    return grid

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

# === Metrics Functions ===

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

# === Visualizer Class ===
class AutomatonVisualizer:
    def __init__(self, grid, wraparound):
        self.grid = grid
        self.wraparound = wraparound
        self.generation = 1
        self.cell_size = 20
        self.n = grid.shape[0]
        self.age_grid = np.zeros_like(grid)

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

        self.next_50_button = tk.Button(self.button_frame, text="Next 50 Generations", font=("Helvetica", 14), command=self.next_50_generations)
        self.next_50_button.pack(side=tk.LEFT, padx=10)

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

        colors = {0: "white", 1: "black", 2: "gray", 3: "blue", 5: "green", 10: "purple"}

        for i in range(self.n):
            for j in range(self.n):
                x0 = j * scale_x + scale_x * 0.25
                y0 = i * scale_y + scale_y * 0.25
                x1 = j * scale_x + scale_x * 0.75
                y1 = i * scale_y + scale_y * 0.75

                if self.grid[i, j] == 0:
                    color = "white"
                else:
                    age = self.age_grid[i, j]
                    if age >= 10:
                        color = colors[10]
                    elif age >= 5:
                        color = colors[5]
                    elif age >= 3:
                        color = colors[3]
                    elif age >= 2:
                        color = colors[2]
                    else:
                        color = colors[1]

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

        for i in range(0, self.n - 1):
            for j in range(0, self.n - 1):
                x0 = j * scale_x
                y0 = i * scale_y
                x1 = x0 + 2 * scale_x
                y1 = y0 + 2 * scale_y
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", dash=(4, 2))

        for i in range(0, self.n + 1, 2):
            y = i * scale_y
            self.canvas.create_line(0, y, self.canvas_width, y, fill="blue", width=2)
        for j in range(0, self.n + 1, 2):
            x = j * scale_x
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="blue", width=2)

        self.update_metrics()

    def update_metrics(self):
        alive_ratio = np.sum(self.grid) / self.grid.size
        variance = np.var(self.grid)
        clusters = count_clusters(self.grid)
        alive_2 = np.sum((self.age_grid >= 2) & (self.grid == 1))
        alive_5 = np.sum((self.age_grid >= 5) & (self.grid == 1))
        alive_10 = np.sum((self.age_grid >= 10) & (self.grid == 1))
        text = (f"Generation: {self.generation}\n"
                f"Alive Ratio: {alive_ratio:.3f}\n"
                f"Variance: {variance:.5f}\n"
                f"Clusters: {clusters}\n"
                f">=2 generations: {alive_2}  >=5 generations: {alive_5}  >=10 generations: {alive_10}")
        self.info_label.config(text=text)

    def next_generation(self):
        new_grid = apply_rules(self.grid, self.wraparound, self.generation)
        self.age_grid = (self.age_grid + 1) * (new_grid == 1)
        self.grid = new_grid
        self.generation += 1
        self.draw_grid()

    def next_50_generations(self):
        for _ in range(50):
            self.next_generation()

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
        
# === Main ===

def main():
    setup_window = tk.Tk()
    setup_window.title("Setup Parameters")
    setup_window.attributes("-fullscreen", True)

    main_frame = tk.Frame(setup_window)
    main_frame.pack(pady=100)

    tk.Label(main_frame, text="Choose initial probability:", font=("Helvetica", 16)).pack(pady=5)
    prob_var = tk.StringVar(value="0.5")
    prob_menu = ttk.Combobox(main_frame, textvariable=prob_var, values=["0.25", "0.5", "0.75"], state="readonly", font=("Helvetica", 14))
    prob_menu.pack()

    tk.Label(main_frame, text="Enable wraparound?", font=("Helvetica", 16)).pack(pady=5)
    wrap_var = tk.StringVar(value="yes")
    wrap_menu = ttk.Combobox(main_frame, textvariable=wrap_var, values=["yes", "no"], state="readonly", font=("Helvetica", 14))
    wrap_menu.pack()

    tk.Label(main_frame, text="Enter grid size (positive integer):", font=("Helvetica", 16)).pack(pady=5)
    grid_size_var = tk.StringVar(value="100")
    grid_size_entry = tk.Entry(main_frame, textvariable=grid_size_var, font=("Helvetica", 14))
    grid_size_entry.pack()

    tk.Label(main_frame, text="Choose initial state:", font=("Helvetica", 16)).pack(pady=5)
    state_var = tk.StringVar(value="random")
    state_menu = ttk.Combobox(main_frame, textvariable=state_var, values=["random", "sparse", "glider", "blinker", "oscillator"], state="readonly", font=("Helvetica", 14))
    state_menu.pack()

    def start_simulation():
        try:
            prob = float(prob_var.get())
            wraparound = wrap_var.get().lower() == "yes"
            grid_size = int(grid_size_var.get())
            if grid_size <= 0:
                raise ValueError("Grid size must be a positive integer")

            initial_state = state_var.get()

            if initial_state in ["glider", "blinker", "oscillator"]:
                grid = initialize_grid(grid_size, mode=initial_state)
            else:
                grid = initialize_grid(grid_size, prob, mode=initial_state)
            
            setup_window.destroy()

            if initial_state == "Glider":
                grid = initialize_grid(grid_size, prob=prob, mode="glider")
            elif initial_state == "Random":
                grid = initialize_grid(grid_size, prob=prob, mode="random")
            else:  # Sparse
                grid = initialize_grid(grid_size, prob=prob, mode="sparse")

            AutomatonVisualizer(grid, wraparound)
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(main_frame, text="Start Simulation", font=("Helvetica", 16), command=start_simulation).pack(pady=20)
    tk.Button(main_frame, text="Exit", font=("Helvetica", 16), command=setup_window.destroy).pack()

    setup_window.mainloop()

if __name__ == "__main__":
    main()