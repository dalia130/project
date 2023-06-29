from django.shortcuts import render
from django.conf import settings
import random
from collections import defaultdict

def find_stages(operation_dependencies, operation_durations, num_solutions):
    in_degree = defaultdict(int)
    for dependencies in operation_dependencies.values():
        for dependency in dependencies:
            in_degree[dependency] += 1

    solutions = []
    stack = []
    initial_state = ([], list(operation_dependencies.keys()), {})
    stack.append(initial_state)

    while stack and len(solutions) < num_solutions:
        current_stage, available_ops, completed_durations = stack.pop()
        if len(current_stage) == len(operation_dependencies):
            solutions.append((current_stage, sum(completed_durations.values())))
            continue

        random.shuffle(available_ops)  # Randomize the order of available operations

        for op in available_ops:
            dependencies = operation_dependencies[op]
            if all(dep in completed_durations for dep in dependencies):
                new_stage = current_stage + [op]
                new_durations = completed_durations.copy()
                new_durations[op] = operation_durations[op]
                new_available_ops = [o for o in available_ops if o != op]
                stack.append((new_stage, new_available_ops, new_durations))

    return solutions


def calculate_metrics(solution):
    steps = len(solution[0])
    total_time = solution[1]
    differences = [abs(total_time - sum(operation_durations[op] for op in step)) for step in solution[0]]
    total_differences = sum(differences)
    avg_differences = total_differences / steps
    max_time = max(sum(operation_durations[op] for op in step) for step in solution[0])
    min_time = min(sum(operation_durations[op] for op in step) for step in solution[0])
    return total_time, total_differences, avg_differences, max_time, min_time


def save_solution(filename, solution):
    with open(filename, 'w') as file:
        file.write(f"Solution 1 :\n")
        for i, step in enumerate(solution[0], start=1):
            step_time = sum(operation_durations[op] for op in step)
            file.write(f"{i} : {step} Total Time=({step_time}), dif=0.00\n")
        file.write(f"Total Time= {solution[1]}\n")

# Read from files and convert to the desired format for the algorithm
with open("tasks.txt", "r") as tasks_file:
    tasks_data = tasks_file.read()
operation_durations = {eval("[" + st + "]")[0]: eval("[" + st + "]")[1] for st in tasks_data.split("\n")}

operation_dependencies = {}

# Read the file
with open("tasks_links.txt", "r") as file:
    lines = file.readlines()

# Process each line and build the dictionary
for line in lines:
    dependency, task = map(int, line.strip().split(","))
    if task not in operation_dependencies:
        operation_dependencies[task] = []
    if dependency not in operation_dependencies:
        operation_dependencies[dependency] = []
    operation_dependencies[task].append(dependency)
operation_dependencies = dict(sorted(operation_dependencies.items()))

num_solutions = 10
results = find_stages(operation_dependencies, operation_durations, num_solutions)

# Find the best solution from the generated solutions
best_solution = min(results, key=lambda x: x[1])

# Save the results to files
save_solution("output.txt", random.choice(results))
save_solution("all_results.txt", best_solution)
save_solution("optimal_solution.txt", best_solution)


def index(request):
    # Read from files and convert to the desired format for the algorithm
    with open(settings.BASE_DIR / "tasks.txt", "r") as tasks_file:
        tasks_data = tasks_file.read()
    operation_durations = {eval("[" + st + "]")[0]: eval("[" + st + "]")[1] for st in tasks_data.split("\n")}

    operation_dependencies = {}

    # Read the file
    with open(settings.BASE_DIR / "tasks_links.txt", "r") as file:
        lines = file.readlines()

    # Process each line and build the dictionary
    for line in lines:
        dependency, task = map(int, line.strip().split(","))
        if task not in operation_dependencies:
            operation_dependencies[task] = []
        if dependency not in operation_dependencies:
            operation_dependencies[dependency] = []
        operation_dependencies[task].append(dependency)
    operation_dependencies = dict(sorted(operation_dependencies.items()))

    num_solutions = 10
    results = find_stages(operation_dependencies, operation_durations, num_solutions)

    # Find the best solution from the generated solutions
    best_solution = min(results, key=lambda x: x[1])

    # Save the results to files
    save_solution(settings.BASE_DIR / "output.txt", random.choice(results))
    save_solution(settings.BASE_DIR / "all_results.txt", best_solution)
    save_solution(settings.BASE_DIR / "optimal_solution.txt", best_solution)

    context = {
        'best_solution': best_solution,
    }
    return render(request, 'index.html', context)
