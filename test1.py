import streamlit as st
import random
from typing import List, Tuple, Dict

# Constants
DAYS_IN_WEEK = 7
HOURS_IN_SHIFT = 8
ZONES = ['A', 'B', 'C']
SKILLS = ['fire', 'fighting', 'camera', 'maintenance']
SHIFT_TYPES = ['day_early', 'day_late', 'night']

class Agent:
    def __init__(self, id: int, hours_per_week: int, skills: List[str]):
        self.id = id
        self.hours_per_week = hours_per_week
        self.skills = skills
        self.schedule = [[] for _ in range(DAYS_IN_WEEK)]

class Intervention:
    def __init__(self, client_id: int, skill_required: str, zone: str, shift_type: str, duration: int):
        self.client_id = client_id
        self.skill_required = skill_required
        self.zone = zone
        self.shift_type = shift_type
        self.duration = duration

class TimetableGeneticAlgorithm:
    def __init__(self, agents: List[Agent], interventions: List[Intervention], population_size: int, generations: int):
        self.agents = agents
        self.interventions = interventions
        self.population_size = population_size
        self.generations = generations

    def generate_initial_population(self) -> List[Dict]:
        population = []
        for _ in range(self.population_size):
            timetable = {agent.id: [[] for _ in range(DAYS_IN_WEEK)] for agent in self.agents}
            for intervention in self.interventions:
                agent = self.select_random_suitable_agent(intervention)
                day = random.randint(0, DAYS_IN_WEEK - 1)
                timetable[agent.id][day].append(intervention)
            population.append(timetable)
        return population

    def select_random_suitable_agent(self, intervention: Intervention) -> Agent:
        suitable_agents = [agent for agent in self.agents if intervention.skill_required in agent.skills]
        return random.choice(suitable_agents) if suitable_agents else random.choice(self.agents)

    def fitness(self, timetable: Dict) -> float:
        score = 0
        for agent_id, schedule in timetable.items():
            agent = next(a for a in self.agents if a.id == agent_id)
            total_hours = sum(intervention.duration for day in schedule for intervention in day)
            if total_hours <= agent.hours_per_week:
                score += 1
            # Add more constraint checks here
        return score

    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        child = {agent.id: [[] for _ in range(DAYS_IN_WEEK)] for agent in self.agents}
        for agent_id in child:
            for day in range(DAYS_IN_WEEK):
                if random.random() < 0.5:
                    child[agent_id][day] = parent1[agent_id][day].copy()
                else:
                    child[agent_id][day] = parent2[agent_id][day].copy()
        return child

    def mutate(self, timetable: Dict) -> Dict:
        if random.random() < 0.1:  # 10% chance of mutation
            agent1, agent2 = random.sample(list(timetable.keys()), 2)
            day = random.randint(0, DAYS_IN_WEEK - 1)
            timetable[agent1][day], timetable[agent2][day] = timetable[agent2][day], timetable[agent1][day]
        return timetable

    def select_parents(self, population: List[Dict]) -> Tuple[Dict, Dict]:
        tournament_size = 5
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=self.fitness), max(tournament, key=self.fitness)

    def evolve(self):
        population = self.generate_initial_population()
        for generation in range(self.generations):
            new_population = []
            for _ in range(self.population_size):
                parent1, parent2 = self.select_parents(population)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            population = new_population
            best_timetable = max(population, key=self.fitness)
            yield generation, best_timetable, self.fitness(best_timetable)

def main():
    st.title("Security Agent Timetabling with Genetic Algorithm")

    # Sidebar for input parameters
    st.sidebar.header("Parameters")
    population_size = st.sidebar.slider("Population Size", 10, 100, 50)
    generations = st.sidebar.slider("Number of Generations", 10, 500, 100)

    # Create agents and interventions
    agents = [
        Agent(1, 40, ['fire']),
        Agent(2, 40, ['fighting']),
        Agent(3, 40, ['maintenance']),
        Agent(4, 40, ['fire', 'maintenance']),
        Agent(5, 32, [])
    ]

    interventions = [
        Intervention(1, 'fire', 'A', 'day_early', 4),
        Intervention(2, 'fighting', 'B', 'night', 6),
        Intervention(3, 'camera', 'C', 'day_late', 3),
        Intervention(4, 'maintenance', 'A', 'day_early', 5)
    ]

    # Initialize genetic algorithm
    ga = TimetableGeneticAlgorithm(agents, interventions, population_size, generations)

    # Run evolution
    if st.button("Generate Timetable"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        best_fitness_plot = st.line_chart()

        for generation, best_timetable, fitness in ga.evolve():
            progress = (generation + 1) / generations
            progress_bar.progress(progress)
            status_text.text(f"Generation {generation + 1}/{generations}: Best fitness = {fitness}")
            best_fitness_plot.add_rows([fitness])

        st.success("Timetable generation completed!")
        st.subheader("Best Timetable")
        for agent_id, schedule in best_timetable.items():
            st.write(f"Agent {agent_id}:")
            for day, interventions in enumerate(schedule):
                st.write(f"  Day {day + 1}: {', '.join(str(i.client_id) for i in interventions)}")

if __name__ == "__main__":
    main()