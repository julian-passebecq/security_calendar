import streamlit as st
import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# Constants
DAYS_IN_WEEK = 7
HOURS_IN_SHIFT = 8
ZONES = ['A', 'B', 'C', 'HQ']
SKILLS = ['fire', 'fighting', 'camera', 'maintenance']
SHIFT_TYPES = ['day_early', 'day_late', 'night']


class Agent:
    def __init__(self, id: int, hours_per_week: int, skills: List[str]):
        self.id = id
        self.hours_per_week = hours_per_week
        self.skills = skills
        self.schedule = [[] for _ in range(DAYS_IN_WEEK)]
        self.night_shifts = 0


class Intervention:
    def __init__(self, client_id: int, skill_required: str, zone: str, shift_type: str, duration: int):
        self.client_id = client_id
        self.skill_required = skill_required
        self.zone = zone
        self.shift_type = shift_type
        self.duration = duration


class Timeslot:
    def __init__(self, day: int, start_time: datetime, duration: int, intervention: Intervention):
        self.day = day
        self.start_time = start_time
        self.duration = duration
        self.intervention = intervention


class TimetableGeneticAlgorithm:
    def __init__(self, agents: List[Agent], interventions: List[Intervention], population_size: int, generations: int):
        self.agents = agents
        self.interventions = interventions
        self.population_size = population_size
        self.generations = generations

    def generate_initial_population(self) -> List[Dict[int, List[Timeslot]]]:
        population = []
        for _ in range(self.population_size):
            timetable = {agent.id: [] for agent in self.agents}
            for intervention in self.interventions:
                agent = self.select_random_suitable_agent(intervention)
                day = random.randint(0, DAYS_IN_WEEK - 1)
                start_time = self.get_random_start_time(intervention.shift_type)
                timeslot = Timeslot(day, start_time, intervention.duration, intervention)
                timetable[agent.id].append(timeslot)
            population.append(timetable)
        return population

    def select_random_suitable_agent(self, intervention: Intervention) -> Agent:
        suitable_agents = [agent for agent in self.agents if intervention.skill_required in agent.skills]
        return random.choice(suitable_agents) if suitable_agents else random.choice(self.agents)

    def get_random_start_time(self, shift_type: str) -> datetime:
        if shift_type == 'day_early':
            return datetime.now().replace(hour=5, minute=0) + timedelta(minutes=random.randint(0, 240))
        elif shift_type == 'day_late':
            return datetime.now().replace(hour=12, minute=0) + timedelta(minutes=random.randint(0, 240))
        else:  # night shift
            return datetime.now().replace(hour=22, minute=0) + timedelta(minutes=random.randint(0, 240))

    def fitness(self, timetable: Dict[int, List[Timeslot]]) -> float:
        score = 0
        for agent_id, timeslots in timetable.items():
            agent = next(a for a in self.agents if a.id == agent_id)

            # Check total hours
            total_hours = sum(slot.duration for slot in timeslots)
            if total_hours <= agent.hours_per_week:
                score += 1
            else:
                score -= (total_hours - agent.hours_per_week) / 2

            # Check skills match
            if all(slot.intervention.skill_required in agent.skills for slot in timeslots):
                score += 2

            # Check for overlapping timeslots
            timeslots.sort(key=lambda x: (x.day, x.start_time))
            for i in range(len(timeslots) - 1):
                if timeslots[i].day == timeslots[i + 1].day:
                    end_time = timeslots[i].start_time + timedelta(hours=timeslots[i].duration)
                    if end_time > timeslots[i + 1].start_time:
                        score -= 1

            # Check for proper breaks
            for i in range(len(timeslots) - 1):
                if timeslots[i].day == timeslots[i + 1].day:
                    break_time = (timeslots[i + 1].start_time - (timeslots[i].start_time + timedelta(
                        hours=timeslots[i].duration))).total_seconds() / 3600
                    if break_time < 0.5:  # Less than 30 minutes break
                        score -= 1
                    elif break_time > 1 and break_time < 8:  # Break between 1 and 8 hours
                        score -= 0.5

            # Check night shift constraints
            night_shifts = sum(1 for slot in timeslots if slot.intervention.shift_type == 'night')
            if night_shifts <= 2:
                score += 1
            else:
                score -= (night_shifts - 2)

        return max(score, 0)  # Ensure non-negative score

    def crossover(self, parent1: Dict[int, List[Timeslot]], parent2: Dict[int, List[Timeslot]]) -> Dict[
        int, List[Timeslot]]:
        child = {agent_id: [] for agent_id in parent1.keys()}
        for agent_id in child:
            split_point = random.randint(0, len(parent1[agent_id]))
            child[agent_id] = parent1[agent_id][:split_point] + parent2[agent_id][split_point:]
        return child

    def mutate(self, timetable: Dict[int, List[Timeslot]]) -> Dict[int, List[Timeslot]]:
        if random.random() < 0.1:  # 10% chance of mutation
            agent_ids = list(timetable.keys())
            agent1, agent2 = random.sample(agent_ids, 2)
            if timetable[agent1] and timetable[agent2]:
                slot_index1 = random.randint(0, len(timetable[agent1]) - 1)
                slot_index2 = random.randint(0, len(timetable[agent2]) - 1)
                timetable[agent1][slot_index1], timetable[agent2][slot_index2] = timetable[agent2][slot_index2], \
                timetable[agent1][slot_index1]
        return timetable

    def select_parents(self, population: List[Dict[int, List[Timeslot]]]) -> Tuple[
        Dict[int, List[Timeslot]], Dict[int, List[Timeslot]]]:
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

    st.sidebar.header("Parameters")
    population_size = st.sidebar.slider("Population Size", 10, 200, 100)
    generations = st.sidebar.slider("Number of Generations", 10, 1000, 200)

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
        Intervention(4, 'maintenance', 'A', 'day_early', 5),
        Intervention(5, 'fire', 'B', 'day_late', 4),
        Intervention(6, 'maintenance', 'C', 'night', 5),
        Intervention(7, 'camera', 'HQ', 'day_early', 4),
        Intervention(8, 'fighting', 'A', 'night', 6),
    ]

    ga = TimetableGeneticAlgorithm(agents, interventions, population_size, generations)

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
        for agent_id, timeslots in best_timetable.items():
            st.write(f"Agent {agent_id}:")
            for timeslot in sorted(timeslots, key=lambda x: (x.day, x.start_time)):
                st.write(
                    f"  Day {timeslot.day + 1}, {timeslot.start_time.strftime('%H:%M')}: Client {timeslot.intervention.client_id} ({timeslot.intervention.skill_required}, {timeslot.duration}h)")


if __name__ == "__main__":
    main()