from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus
import pandas as pd
from datetime import datetime, timedelta

def time_diff_in_hours(t1, t2):
    """Calculate the difference in hours between two times, considering overnight shifts."""
    t1 = datetime.combine(datetime.today(), t1)
    t2 = datetime.combine(datetime.today(), t2)
    if t2 < t1:
        t2 += timedelta(days=1)
    return (t2 - t1).seconds / 3600

def generate_roster(shift_demands, staffing_rules):
    """Generate the roster using linear programming."""
    # Define the problem
    prob = LpProblem("Roster_Optimization", LpMinimize)

    # Create decision variables
    staff = staffing_rules['Name'].unique()
    shifts = shift_demands['Shift Type'].unique()
    days = shift_demands['Day'].unique()
    shift_details = {shift: shift_demands[shift_demands['Shift Type'] == shift].iloc[0] for shift in shifts}

    # Decision variables for each employee, day, and shift
    x = LpVariable.dicts("shift", (staff, days, shifts), 0, 1, cat='Binary')

    # Add objective function (minimize the total number of shifts)
    prob += lpSum(x[emp][day][shift] for emp in staff for day in days for shift in shifts)

    # Add shift demand constraints
    for _, row in shift_demands.iterrows():
        day = row['Day']
        shift = row['Shift Type']
        skill = row['Skill']
        demand = row['Number of Staff Required']
        
        # Ensure enough staff with the correct skill
        prob += lpSum(x[emp][day][shift] for emp in staff 
                      if staffing_rules[(staffing_rules['Name'] == emp) & (staffing_rules['Skill'] == skill)].any(axis=None)) == demand

    # Max shifts per day
    for emp in staff:
        for day in days:
            prob += lpSum(x[emp][day][shift] for shift in shifts) <= 1

    # Min hours per roster (simplified)
    for emp in staff:
        total_hours_per_shift = {shift: time_diff_in_hours(shift_details[shift]['Start Time'], shift_details[shift]['End Time']) for shift in shifts}
        prob += lpSum(x[emp][day][shift] * total_hours_per_shift[shift] for day in days for shift in shifts) >= 192

    # Solve the problem
    prob.solve()

    # Print solver status and variable values for debugging
    print("Status:", LpStatus[prob.status])
    if LpStatus[prob.status] == "Infeasible":
        print("The following constraints could not be satisfied:")
        for name, c in prob.constraints.items():
            if c.value() > c.constant:
                print(f"Constraint {name} is unsatisfied by {c.value() - c.constant}")
        for v in prob.variables():
            if v.varValue is not None and v.varValue > 0:
                print(f"{v.name} = {v.varValue}")

    # Check for duplicate assignments
    assigned_shifts = {}
    for emp in staff:
        assigned_shifts[emp] = {day: [] for day in days}
        for day in days:
            for shift in shifts:
                if x[emp][day][shift].varValue == 1:
                    if len(assigned_shifts[emp][day]) > 0:
                        print(f"Duplicate shift assignment for {emp} on {day}: {assigned_shifts[emp][day]} and {shift}")
                    assigned_shifts[emp][day].append(shift)

    # Extract the results
    roster = []
    for emp in staff:
        for day in days:
            for shift in shifts:
                if x[emp][day][shift].varValue == 1:
                    roster.append([emp, day, shift])

    return pd.DataFrame(roster, columns=['Employee', 'Day', 'Shift Type'])
