import pandas as pd

def main():
    # File path to the input Excel file
    input_file = 'data/sample_data.xlsx'
    output_file = 'data/generated_roster.xlsx'

    # Read input data
    shift_demands = read_shift_demands(input_file)
    staffing_rules = read_staffing_rules(input_file)

    # Print columns of input DataFrames for debugging
    print("Shift Demands columns:", shift_demands.columns)
    print("Staffing Rules columns:", staffing_rules.columns)

    # Validate input data
    validate_shift_demands(shift_demands)
    validate_staffing_rules(staffing_rules)

    # Generate roster using the existing logic (assumed to be implemented)
    roster = generate_roster(shift_demands, staffing_rules)

    # Check for duplicate entries before merging
    if roster.duplicated(subset=['Employee', 'Day']).any():
        print("Warning: Duplicate entries found in the roster")
        print(roster[roster.duplicated(subset=['Employee', 'Day'], keep=False)])

        # Option 1: Remove duplicates
        # roster = roster.drop_duplicates(subset=['Employee', 'Day'])

        # Option 2: Handle duplicates based on specific logic
        # (e.g., prioritize certain shifts, aggregate data, etc.)
        # This needs custom logic based on your specific requirements

    # Create an empty DataFrame with the same structure for merging
    employees = staffing_rules['Name'].unique()
    days = shift_demands['Day'].unique()
    empty_df = pd.DataFrame([(emp, day) for emp in employees for day in days], columns=['Employee', 'Day'])
    
    # Merge and pivot
    formatted_roster = empty_df.merge(roster, on=['Employee', 'Day'], how='left') \
                               .pivot(index='Employee', columns='Day', values='Shift Type').fillna('')

    # Save the formatted roster to Excel
    formatted_roster.to_excel(output_file)

def read_shift_demands(file_path):
    # Read the sheet into a DataFrame
    df = pd.read_excel(file_path, sheet_name='Shift Demands')
    
    # Melt the DataFrame to convert it from wide to long format
    df_melted = df.melt(id_vars=['Shift Type', 'Skill', 'Start Time', 'End Time'],
                        var_name='Day', value_name='Number of Staff Required')
    
    # Remove rows where 'Number of Staff Required' is 0 or NaN
    df_melted = df_melted[df_melted['Number of Staff Required'] > 0].dropna(subset=['Number of Staff Required'])

    return df_melted

def read_staffing_rules(file_path):
    return pd.read_excel(file_path, sheet_name='Staffing Rules')

def validate_shift_demands(df):
    required_columns = ['Shift Type', 'Skill', 'Start Time', 'End Time', 'Day', 'Number of Staff Required']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

def validate_staffing_rules(df):
    required_columns = ['Name', 'Skill', 'Max Shifts Per Day', 'Minimum Hours Per Roster', 'Max Days In A Row', 'Min Days Off In A Row', 'Min Hours Between Shifts']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

def generate_roster(shift_demands, staffing_rules):
    # Placeholder for the roster generation logic
    # Ensure the returned DataFrame has columns: 'Employee', 'Day', 'Shift Type'
    return pd.DataFrame({
        'Employee': ['Alice', 'Alice', 'Bob', 'Bob'],
        'Day': ['Monday', 'Tuesday', 'Monday', 'Tuesday'],
        'Shift Type': ['AM CG RHH', 'PM CG HOS', 'AM CG RHH', 'PM CG HOS']
    })

if __name__ == "__main__":
    main()
