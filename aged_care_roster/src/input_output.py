import pandas as pd

def read_shift_demands(file_path):
    """Read the shift demands from the Excel file."""
    df = pd.read_excel(file_path, sheet_name='Shift Demands')
    shift_demands = []
    for _, row in df.iterrows():
        for day in df.columns[4:]:
            shift_demands.append({
                'Day': day,
                'Shift Type': row['Shift Type'],
                'Skill': row['Skill'],
                'Start Time': row['Start Time'],
                'End Time': row['End Time'],
                'Number of Staff Required': row[day]
            })
    return pd.DataFrame(shift_demands)

def read_staffing_rules(file_path):
    """Read the staffing rules from the Excel file."""
    df = pd.read_excel(file_path, sheet_name='Staffing Rules')
    return df
