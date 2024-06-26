import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Constants
SHIFTS = {
    'Day1': {'start': '05:00', 'end': '13:00'},
    'Day2': {'start': '12:00', 'end': '20:00'},
    'Night': {'start': '21:00', 'end': '05:00'}
}

ZONES = ['A', 'B', 'C', 'HQ']

INTERVENTIONS = ['fire', 'fighting', 'camera', 'maintenance']


# Classes
class Agent:
    def __init__(self, id, name, certifications, hours_per_week):
        self.id = id
        self.name = name
        self.certifications = certifications
        self.hours_per_week = hours_per_week


class Intervention:
    def __init__(self, id, type, zone, duration):
        self.id = id
        self.type = type
        self.zone = zone
        self.duration = duration


# Genetic Algorithm Functions
def create_individual():
    # Create a random schedule for a week
    schedule = np.zeros((7 * 24 * 2, 5), dtype=int)  # 7 days, 24 hours, 30-minute intervals, 5 agents
    # Fill with random interventions
    for day in range(7):
        for agent in range(5):
            if random.random() < 0.7:  # 70% chance of working
                shift = random.choice(list(SHIFTS.keys()))
                start, end = SHIFTS[shift]['start'], SHIFTS[shift]['end']
                start_idx = day * 48 + int(start.split(':')[0]) * 2
                end_idx = day * 48 + int(end.split(':')[0]) * 2
                schedule[start_idx:end_idx, agent] = random.randint(1, 100)  # Random intervention ID
    return schedule


def fitness(individual):
    # Calculate fitness score
    score = 0
    # Add your fitness calculation logic here
    return score


def crossover(parent1, parent2):
    # Implement crossover logic
    child = parent1.copy()
    # Add your crossover logic here
    return child


def mutate(individual):
    # Implement mutation logic
    mutated = individual.copy()
    # Add your mutation logic here
    return mutated


def genetic_algorithm(population_size, generations):
    population = [create_individual() for _ in range(population_size)]

    for gen in range(generations):
        # Selection
        parents = random.choices(population, k=population_size)

        # Crossover
        offspring = [crossover(parents[i], parents[i + 1]) for i in range(0, population_size - 1, 2)]

        # Mutation
        offspring = [mutate(ind) for ind in offspring]

        # Evaluation
        population = sorted(population + offspring, key=fitness, reverse=True)[:population_size]

        # Update progress
        if gen % 10 == 0:
            st.write(f"Generation {gen}: Best fitness = {fitness(population[0])}")

    return population[0]


# Visualization Functions
def plot_schedule(schedule):
    # Create a Gantt chart of the schedule
    df = []
    for day in range(7):
        for agent in range(5):
            interventions = np.where(schedule[day * 48:(day + 1) * 48, agent] > 0)[0]
            for start, end in zip(interventions[:-1], interventions[1:]):
                if end > start + 1:  # Intervention longer than 30 minutes
                    df.append(dict(Task=f"Agent {agent + 1}",
                                   Start=f"2023-01-0{day + 1} {start // 2:02d}:{(start % 2) * 30:02d}:00",
                                   Finish=f"2023-01-0{day + 1} {end // 2:02d}:{(end % 2) * 30:02d}:00",
                                   Resource=f"Intervention {schedule[day * 48 + start, agent]}"))

    fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True)
    st.plotly_chart(fig)


def plot_agent_utilization(schedule):
    # Plot agent utilization
    utilization = np.sum(schedule > 0, axis=0) / (7 * 48)  # 7 days, 48 half-hours per day
    fig = go.Figure(data=[go.Bar(x=[f"Agent {i + 1}" for i in range(5)], y=utilization)])
    fig.update_layout(title="Agent Utilization", xaxis_title="Agent", yaxis_title="Utilization")
    st.plotly_chart(fig)


# Streamlit App
def main():
    st.title("Security Company Scheduler - Genetic Algorithm Approach")

    st.header("Problem Setup")
    st.write("This app uses a genetic algorithm to create a weekly schedule for a security company.")
    st.write("Constraints include agent certifications, shift types, intervention requirements, and travel times.")

    st.header("Genetic Algorithm Parameters")
    population_size = st.slider("Population Size", 10, 1000, 100)
    generations = st.slider("Number of Generations", 10, 1000, 100)

    if st.button("Generate Schedule"):
        with st.spinner("Generating schedule..."):
            best_schedule = genetic_algorithm(population_size, generations)

        st.success("Schedule generated!")

        st.header("Generated Schedule")
        plot_schedule(best_schedule)

        st.header("Agent Utilization")
        plot_agent_utilization(best_schedule)

        st.header("Schedule Analysis")
        st.write("Add more detailed analysis of the generated schedule here.")


if __name__ == "__main__":
    main()