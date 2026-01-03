import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# ---------------- CONFIG ----------------
GRID_SIZE = 2
STEPS = 12
RESOURCE_PROBABILITY = 0.3
MOVE_COST = 1
COLLECT_REWARD = 10
# ---------------------------------------

# Room coordinates
rooms = {
    (0, 1): "Room1",
    (1, 1): "Room2",
    (0, 0): "Room3",
    (1, 0): "Room4"
}

# Environment (Resource / Empty)
environment = {
    pos: "Resource" if random.random() < RESOURCE_PROBABILITY else "Empty"
    for pos in rooms
}

# Agent state
agent_pos = (0, 1)
score = 0
energy = 100

# Performance tracking
score_history = []
energy_history = []
step_history = []

# -------- Reflex Agent ----------
def reflex_agent(state):
    if state == "Resource":
        return "Collect"
    return "Move"

# -------- Move Logic ----------
def move_agent(pos):
    x, y = pos
    moves = []
    if x > 0: moves.append((x - 1, y))
    if x < GRID_SIZE - 1: moves.append((x + 1, y))
    if y > 0: moves.append((x, y - 1))
    if y < GRID_SIZE - 1: moves.append((x, y + 1))
    return random.choice(moves)

# -------- Add Resources ----------
def add_random_resources(env):
    for room in env:
        if random.random() < RESOURCE_PROBABILITY:
            env[room] = "Resource"

# -------- Draw Environment ----------
def draw_environment(env, agent_pos, step):
    fig, ax = plt.subplots()
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Step: {step} | Score: {score} | Energy: {energy}")

    for (x, y), name in rooms.items():
        color = 'orange' if env[(x, y)] == "Resource" else 'gray'
        rect = patches.Rectangle((x, y), 1, 1, facecolor=color, edgecolor='black')
        ax.add_patch(rect)

        ax.text(x + 0.5, y + 0.6, name, ha='center', color='white', fontsize=9)
        ax.text(x + 0.5, y + 0.4, env[(x, y)], ha='center', color='white', fontsize=8)

    # Agent
    ax.add_patch(patches.Circle(
        (agent_pos[0] + 0.5, agent_pos[1] + 0.5),
        0.12,
        color='blue'
    ))

    plt.pause(1)
    plt.close()

# -------- Simulation ----------
plt.ion()

for step in range(1, STEPS + 1):
    state = environment[agent_pos]
    action = reflex_agent(state)

    draw_environment(environment, agent_pos, step)

    if action == "Collect":
        environment[agent_pos] = "Empty"
        score += COLLECT_REWARD
    else:
        agent_pos = move_agent(agent_pos)
        energy -= MOVE_COST

    add_random_resources(environment)

    # Store performance
    step_history.append(step)
    score_history.append(score)
    energy_history.append(energy)

plt.ioff()

# -------- Performance Graph ----------
plt.figure()
plt.plot(step_history, score_history, label="Score")
plt.plot(step_history, energy_history, label="Energy")
plt.xlabel("Steps")
plt.ylabel("Value")
plt.title("Resource Collection Agent Performance")
plt.legend()
plt.grid(True)
plt.show()

print("✅ Simulation Complete")
