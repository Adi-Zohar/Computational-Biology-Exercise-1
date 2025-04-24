import numpy as np
import matplotlib.pyplot as plt


def initialize_grid(size, prob=0.5):
    """
    Initialize a size x size grid with 0/1 values.
    Each cell has a probability `prob` to be 1 (alive).
    """
    return np.random.choice([0, 1], size=(size, size), p=[1 - prob, prob])


def get_block(grid, i, j, wraparound):
    """
    Extract a 2x2 block from the grid starting at position (i, j).
    If wraparound is True, handles edges by wrapping indices.
    If wraparound is False and block is out of bounds, returns None.
    """
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
    """
    Write a 2x2 block to the grid starting at position (i, j).
    Handles edge wrapping if needed.
    """
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
    """
    Apply the block rules to the entire grid.
    - Odd generations use aligned blocks (blue grid).
    - Even generations use offset blocks (red dashed grid).
    """
    n = grid.shape[0]
    new_grid = grid.copy()
    offset = 0 if generation_number % 2 == 1 else 1  # odd: 0, even: 1

    for i in range(offset, n, 2):
        for j in range(offset, n, 2):
            block = get_block(grid, i, j, wraparound)
            if block is None:
                continue
            ones = np.sum(block)
            if ones == 2:
                continue
            block = 1 - block  # flip
            if ones == 3:
                block = np.rot90(block, 2)  # rotate 180 degrees
            set_block(new_grid, block, i, j, wraparound)

    return new_grid


def compute_stability(new_grid, old_grid):
    """
    Compute the percentage of cells that did not change.
    """
    unchanged = np.sum(new_grid == old_grid)
    total = new_grid.size
    return (unchanged / total) * 100


def simulate(grid_size=100, p_alive=0.5, wraparound=False, generations=250):
    """
    Run the simulation for the given number of generations.
    Returns the final grid and a list of stability metrics.
    """
    grid = initialize_grid(grid_size, p_alive)
    stability_list = []

    for gen in range(1, generations + 1):
        new_grid = apply_rules(grid, wraparound, gen)
        stability = compute_stability(new_grid, grid)
        stability_list.append(stability)
        grid = new_grid.copy()

        if gen % 50 == 0 or gen == 1 or gen == generations:
            show_grid(grid, gen)

    return grid, stability_list


def show_grid(grid, generation):
    """
    Display the grid as an image.
    """
    plt.imshow(grid, cmap='gray', interpolation='nearest')
    plt.title(f"Generation {generation}")
    plt.axis('off')
    plt.show()


def plot_stability(stability_list):
    """
    Plot the stability percentage over generations.
    """
    plt.plot(stability_list)
    plt.title("Stability over Generations")
    plt.xlabel("Generation")
    plt.ylabel("Unchanged Cell %")
    plt.grid(True)
    plt.show()


def main():
    print("=== Block Automaton Simulator (Question 1) ===")
    grid_size = 100
    generations = 250

    prob = float(input("Enter initial probability for 1s (e.g., 0.25, 0.5, 0.75): "))
    wrap_input = input("Enable wraparound? (yes/no): ").strip().lower()
    wraparound = wrap_input in ['yes', 'y']

    final_grid, stability = simulate(grid_size, prob, wraparound, generations)
    plot_stability(stability)


if __name__ == "__main__":
    main()