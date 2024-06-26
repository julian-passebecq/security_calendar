import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import random


# (Keep the existing Agent, Client, Task, and TASKS definitions)

# (Keep the existing generate_sample_data and calculate_travel_time functions)

# Add the create_schedule function
def create_schedule(agents, clients):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_shift_start = datetime.strptime("09:00", "%H:%M")
    night_shift_start = datetime.strptime("21:00", "%H:%M")

    for day in days:
        for agent in agents:
            agent.scheduled_hours = 0  # Reset daily hours

        for client in clients:
            if day in client.required_interventions:
                for intervention in client.required_interventions[day]:
                    task = TASKS[intervention]
                    shift_start = night_shift_start if task.shift == 'night' else day_shift_start

                    available_agents = [
                        a for a in agents
                        if (task.required_skill in a.skills or task.required_skill is None) and
                           a.scheduled_hours + task.duration <= 8  # 8-hour workday limit
                    ]

                    if available_agents:
                        agent = min(available_agents, key=lambda a: a.scheduled_hours)
                        travel_time = calculate_travel_time(agent.current_location,
                                                            'HQ' if task.location == 'HQ' else client.zone)

                        start_time = shift_start + timedelta(hours=agent.scheduled_hours)
                        end_time = start_time + timedelta(hours=task.duration)

                        agent.schedule[day].append({
                            'client': client.name,
                            'task': task.type,
                            'start': start_time,
                            'end': end_time,
                            'zone': client.zone if task.location == 'onsite' else 'HQ'
                        })

                        agent.scheduled_hours += task.duration + travel_time.total_seconds() / 3600
                        agent.current_location = 'HQ' if task.location == 'HQ' else client.zone

    return agents


# Add the create_visual_calendar function
def create_visual_calendar(agents):
    data = []
    for agent in agents:
        for day, tasks in agent.schedule.items():
            for task in tasks:
                data.append(dict(Task=agent.name, Start=task['start'], Finish=task['end'],
                                 Resource=f"{task['client']} - {task['task']} ({task['zone']})"))

    fig = ff.create_gantt(data, index_col='Resource', show_colorbar=True, group_tasks=True)
    fig.update_layout(title='Agent Schedules', xaxis_title='Time', yaxis_title='Agent')
    return fig


# Streamlit app
def main():
    st.title("Security Company Scheduler (8-Hour Workdays)")

    agents, clients = generate_sample_data()

    st.header("Agent Information")
    agent_data = [[a.name, ", ".join(a.skills), a.hours_per_week] for a in agents]
    agent_df = pd.DataFrame(agent_data, columns=["Agent", "Skills", "Hours per Week"])
    st.table(agent_df)

    st.header("Client Requirements")
    for client in clients:
        st.subheader(f"{client.name} (Zone {client.zone})")
        client_data = [[day, ", ".join(tasks)] for day, tasks in client.required_interventions.items()]
        client_df = pd.DataFrame(client_data, columns=["Day", "Required Interventions"])
        st.table(client_df)

    if st.button("Generate Schedule"):
        scheduled_agents = create_schedule(agents, clients)

        st.header("Agent Schedules")
        for agent in scheduled_agents:
            st.subheader(f"{agent.name}")
            schedule_data = []
            total_hours = 0
            for day, tasks in agent.schedule.items():
                daily_hours = 0
                for task in tasks:
                    duration = (task['end'] - task['start']).total_seconds() / 3600
                    schedule_data.append([
                        day,
                        task['client'],
                        task['task'],
                        task['zone'],
                        task['start'].strftime("%H:%M"),
                        task['end'].strftime("%H:%M"),
                        f"{duration:.2f}"
                    ])
                    daily_hours += duration
                total_hours += daily_hours
                schedule_data.append([day, "Daily Total", "", "", "", "", f"{daily_hours:.2f}"])
            schedule_data.append(["Weekly Total", "", "", "", "", "", f"{total_hours:.2f}"])
            schedule_df = pd.DataFrame(schedule_data,
                                       columns=["Day", "Client", "Task", "Zone", "Start Time", "End Time", "Hours"])
            st.table(schedule_df)

        st.header("Agent Workload Summary")
        workload_data = [[a.name, sum((task['end'] - task['start']).total_seconds() / 3600
                                      for tasks in a.schedule.values() for task in tasks)]
                         for a in scheduled_agents]
        workload_df = pd.DataFrame(workload_data, columns=["Agent", "Scheduled Hours (including travel)"])
        st.table(workload_df)

        st.header("Schedule Analytics")
        total_tasks = sum(len(tasks) for c in clients for tasks in c.required_interventions.values())
        assigned_tasks = sum(len(tasks) for a in scheduled_agents for tasks in a.schedule.values())
        unassigned_tasks = total_tasks - assigned_tasks

        st.write(f"Total tasks: {total_tasks}")
        st.write(f"Assigned tasks: {assigned_tasks}")
        st.write(f"Unassigned tasks: {unassigned_tasks}")

        total_available_hours = sum(a.hours_per_week for a in agents)
        total_scheduled_hours = sum(workload_data[i][1] for i in range(len(workload_data)))
        utilization_rate = (total_scheduled_hours / total_available_hours) * 100
        st.write(f"Agent Utilization Rate: {utilization_rate:.2f}%")

        st.header("Visual Calendar")
        fig = create_visual_calendar(scheduled_agents)
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()