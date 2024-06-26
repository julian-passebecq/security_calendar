import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Define shift types
SHIFTS = {
    'Day1': {'start': '06:00', 'end': '14:00'},
    'Day2': {'start': '09:00', 'end': '17:00'},
    'Night1': {'start': '18:00', 'end': '02:00'},
    'Night2': {'start': '22:00', 'end': '06:00'}
}

# Data models (keep existing Agent and Client classes)

# Define tasks
TASKS = {
    'firecheck': {'duration': 2, 'required_skill': 'fire_certification', 'shift': 'day'},
    'fighting': {'duration': 4, 'required_skill': 'fighting_diploma', 'shift': 'night'},
    'security_camera': {'duration': 2, 'required_skill': None, 'shift': 'any'},
    'night_security': {'duration': 4, 'required_skill': None, 'shift': 'night'}
}


# Manually adjusted sample data generation
def generate_sample_data():
    agents = [
        Agent(1, "Agent 1", ['fire_certification', 'fighting_diploma'], 40, 'Day1'),
        Agent(2, "Agent 2", ['fire_certification'], 40, 'Day2'),
        Agent(3, "Agent 3", ['fighting_diploma'], 40, 'Night1'),
        Agent(4, "Agent 4", [], 40, 'Night2'),
        Agent(5, "Agent 5", [], 32, 'Day1')
    ]

    clients = [
        Client(1, "Client 1", {
            'Monday': ['firecheck', 'security_camera'],
            'Tuesday': ['security_camera', 'night_security'],
            'Wednesday': ['firecheck', 'security_camera'],
            'Thursday': ['security_camera', 'night_security'],
            'Friday': ['firecheck', 'security_camera']
        }, 'A'),
        Client(2, "Client 2", {
            'Monday': ['night_security', 'fighting'],
            'Tuesday': ['security_camera', 'firecheck'],
            'Wednesday': ['night_security', 'fighting'],
            'Thursday': ['security_camera', 'firecheck'],
            'Friday': ['night_security', 'fighting']
        }, 'B'),
        Client(3, "Client 3", {
            'Monday': ['security_camera', 'firecheck'],
            'Tuesday': ['night_security', 'fighting'],
            'Wednesday': ['security_camera', 'firecheck'],
            'Thursday': ['night_security', 'fighting'],
            'Friday': ['security_camera', 'firecheck']
        }, 'C'),
        # Add more clients with balanced day and night tasks
    ]

    return agents, clients


# Improved scheduling function
def create_schedule(agents, clients):
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        for client in clients:
            for task_type in client.required_interventions[day]:
                task = TASKS[task_type]
                shift_type = 'night' if task['shift'] == 'night' else 'day'
                available_agents = [
                    a for a in agents
                    if (task['required_skill'] in a.skills or task['required_skill'] is None) and
                       ((shift_type == 'night' and a.shift_type.startswith('Night')) or
                        (shift_type == 'day' and a.shift_type.startswith('Day'))) and
                       a.scheduled_hours + task['duration'] <= a.hours_per_week
                ]
                if available_agents:
                    agent = min(available_agents, key=lambda a: a.scheduled_hours)
                    shift = SHIFTS[agent.shift_type]
                    start_time = datetime.strptime(shift['start'], "%H:%M")
                    end_time = start_time + timedelta(hours=task['duration'])
                    if end_time > datetime.strptime(shift['end'], "%H:%M"):
                        continue  # Skip if task doesn't fit in shift
                    agent.schedule[day].append({
                        'client': client.name,
                        'task': task_type,
                        'start': start_time.strftime("%H:%M"),
                        'end': end_time.strftime("%H:%M")
                    })
                    agent.scheduled_hours += task['duration']
    return agents


# Streamlit app (keep existing main function)

if __name__ == "__main__":
    main()