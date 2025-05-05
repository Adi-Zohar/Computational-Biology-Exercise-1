import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab

# === Core Functions ===

def initialize_random_grid(size, prob=0.5):
    return np.random.choice([0, 1], size=(size, size), p=[1 - prob, prob])

def insert_form(g, form, startX, startY, sizeX, sizeY):
    
    g[startX:startX + sizeX, startY:startY + sizeY] = form

def initialize_grid(size, mode, wraparound, prob=0.5):
    if mode == 'random':
        return np.random.choice([0, 1], size=(size, size), p=[1 - prob, prob])
    else:
        grid = np.zeros((size, size), dtype=int)
        if not wraparound:
            for i in range(0, size, 2):
                wrap = np.array([
                [1, 0],
                [0, 1]
                ])
                insert_form(grid, wrap,  i, 0, 2, 2)
                insert_form(grid, wrap,  0, i, 2, 2)
                insert_form(grid, wrap,  i, size - 2, 2, 2)
                insert_form(grid, wrap,  size - 2, i, 2, 2)
        if mode == 'glider1':
            glider = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [1, 0, 1, 0]
            ])
            insert_form(grid, glider,  size // 2 + 1, size // 2 + 1, 4, 4)
        elif mode == 'blinker1':
            blinker = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
            ])
            insert_form(grid, blinker, size // 2 + 1, size // 2 + 1, 4, 4)

        elif mode == 'blinker2':
            blinker = np.array([
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1]
            ])
            insert_form(grid, blinker, size // 2 + 1, size // 2 + 1, 4, 4)

        elif mode == 'blinker3':
            blinker = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
            ])
            insert_form(grid, blinker, size // 2 + 1, size // 2 + 1, 4, 4)

        return grid

def get_block(grid, i, j, wraparound):
    n = grid.shape[0]
    if wraparound:
        iModn = i % n
        iPOneModn = (i + 1) % n
        jModn = j % n
        jPOneModn = (j + 1) % n
        return np.array([
            [grid[iModn, jModn], grid[iModn, jPOneModn]],
            [grid[iPOneModn, jModn], grid[iPOneModn, jPOneModn]]
        ])
    else:
        if i + 1 >= n or j + 1 >= n:
            return None
        return grid[i:i + 2, j:j + 2]

def set_block(grid, block, i, j, wraparound):
    n = grid.shape[0]
    if wraparound:
        iModn = i % n
        iPOneModn = (i + 1) % n
        jModn = j % n
        jPOneModn = (j + 1) % n
        grid[iModn, jModn] = block[0, 0]
        grid[iModn, jPOneModn] = block[0, 1]
        grid[iPOneModn, jModn] = block[1, 0]
        grid[iPOneModn, jPOneModn] = block[1, 1]
    else:
        if i + 1 < n and j + 1 < n:
            grid[i:i + 2, j:j + 2] = block

def apply_rules(grid, wraparound, generation_number):
    n = grid.shape[0]
    offset = 1 - (generation_number % 2)

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
            set_block(grid, block, i, j, wraparound)

    return grid

# === Visualizer Class ===
class AutomatonVisualizer:
    def __init__(self, root, grid, wraparound):
        self.root = root
        self.grid = grid
        self.wraparound = wraparound
        self.generation = 1
        self.cell_size = 20
        self.n = grid.shape[0]
        self.avrageAliveRatio = 0
        # self.age_grid = np.zeros_like(grid)

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

        for i in range(self.n):
            iQuarter = i + 0.25
            iTreeQuarter = i + 0.75
            y0 = iQuarter * scale_y
            y1 = iTreeQuarter * scale_y
            for j in range(self.n):
                jQuarter = j + 0.25
                jTreeQuarter = j + 0.75
                exist = self.grid[i, j]
                x0 = jQuarter * scale_x
                x1 = jTreeQuarter * scale_x
                if exist:
                    color = "black"
                else:
                    color = "white"

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
            

                if i % 2:
                    if j % 2:
                        yRed0 = i * scale_y
                        yRed1 = yRed0 + 2 * scale_y
                        xRed0 = j * scale_x
                        xRed1 = xRed0 + 2 * scale_x
                        self.canvas.create_rectangle(xRed0, yRed0, xRed1, yRed1, outline="red", dash=(4, 2))
                    elif j == 0:
                        yRed0 = i * scale_y
                        yRed1 = yRed0 + 2 * scale_y
                        xRed0 = j * scale_x
                        xRed1 = xRed0 + scale_x
                        self.canvas.create_rectangle(xRed0, yRed0, xRed1, yRed1, outline="red", dash=(4, 2))
                elif i == 0:
                    if j > 0:
                        yRed0 = i * scale_y
                        yRed1 = yRed0 + scale_y
                        xRed0 = j * scale_x
                        xRed1 = xRed0 + 2 * scale_x
                        self.canvas.create_rectangle(xRed0, yRed0, xRed1, yRed1, outline="red", dash=(4, 2))
                    else:
                        yRed0 = i * scale_y
                        yRed1 = yRed0 + scale_y
                        xRed0 = j * scale_x
                        xRed1 = xRed0 + scale_x
                        self.canvas.create_rectangle(xRed0, yRed0, xRed1, yRed1, outline="red", dash=(4, 2))


            if i % 2 == 0:
                y = i * scale_y
                x = i * scale_x
                self.canvas.create_line(0, y, self.canvas_width, y, fill="blue", width=2)
                self.canvas.create_line(x, 0, x, self.canvas_height, fill="blue", width=2)
        self.canvas.create_line(0, self.canvas_height, self.canvas_width, self.canvas_height, fill="blue", width=2)
        self.canvas.create_line(self.canvas_width, 0, self.canvas_width, self.canvas_height, fill="blue", width=2)
        self.canvas.create_line(0, 0, 0, self.canvas_height, fill="blue", width=2)

        self.update_metrics()

    def update_metrics(self):
        alive_ratio = np.sum(self.grid) / self.grid.size
        variance = np.var(self.grid)
        self.avrageAliveRatio = (self.avrageAliveRatio * (self.generation - 1) + alive_ratio) / self.generation
        text = (f"Generation: {self.generation}\n"
                f"Alive Ratio: {alive_ratio:.3f}\n"
                f"Variance: {variance:.5f}\n"
                f"Avrage Alive Ratio: {self.avrageAliveRatio:.5f}\n"
                )
        self.info_label.config(text=text)

    def next_generation(self):
        new_grid = apply_rules(self.grid, self.wraparound, self.generation)
        self.grid = new_grid
        self.generation += 1

        # Ensure the GUI updates fully before moving to next generation
        self.root.update_idletasks()
        self.root.update()
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
        
def start():
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
    state_menu = ttk.Combobox(main_frame, textvariable=state_var, values=["random", "glider1", "blinker1", "blinker2", "blinker3"], state="readonly", font=("Helvetica", 14))
    state_menu.pack()

    def start_simulation():
        try:
            prob = float(prob_var.get())
            wraparound = wrap_var.get().lower() == "yes"
            grid_size = int(grid_size_var.get())
            if grid_size <= 0:
                raise ValueError("Grid size must be a positive integer")

            initial_state = state_var.get()

            if initial_state == "glider" or initial_state == "blinker":
                grid = initialize_grid(grid_size, initial_state, wraparound)
            else:
                grid = initialize_grid(grid_size, initial_state, wraparound, prob)
            
            setup_window.destroy()

            AutomatonVisualizer(setup_window, grid, wraparound)
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(main_frame, text="Start Simulation", font=("Helvetica", 16), command=start_simulation).pack(pady=20)
    tk.Button(main_frame, text="Exit", font=("Helvetica", 16), command=setup_window.destroy).pack()

    setup_window.mainloop()

if __name__ == "__main__":
    start()