import pandas as pd

def run(file_path):
    # Load Excel file
    xls = pd.ExcelFile(file_path)
    
    # Read attendance and student data
    attendance_df = pd.read_excel(xls, sheet_name="Attendance_data")
    student_df = pd.read_excel(xls, sheet_name="Student_data")
    
    # Convert 'attendance_date' to datetime format
    attendance_df["attendance_date"] = pd.to_datetime(attendance_df["attendance_date"])

    # Sort data by student_id and date
    attendance_df = attendance_df.sort_values(by=["student_id", "attendance_date"])

    # Identify absence streaks
    attendance_df["is_absent"] = attendance_df["status"] == "Absent"
    attendance_df["absence_group"] = (attendance_df["is_absent"] != attendance_df["is_absent"].shift()).cumsum()

    # Filter out only absence streaks
    absences = attendance_df[attendance_df["is_absent"]].copy()

    # Group by absence streaks to get the start and end dates
    absence_streaks = absences.groupby(["student_id", "absence_group"]).agg(
        absence_start_date=("attendance_date", "first"),
        absence_end_date=("attendance_date", "last"),
        total_absent_days=("attendance_date", "count")
    ).reset_index()

    # Drop the temporary column
    absence_streaks = absence_streaks.drop(columns=["absence_group"])

    # Merge with student details
    final_output = absence_streaks.merge(student_df, on="student_id", how="left")

    # Reorder columns to match expected output
    final_output = final_output[["student_id", "student_name", "absence_start_date", "absence_end_date", "total_absent_days", "parent_email"]]

    return final_output

if __name__ == "__main__":
    file_path = input("Enter the path to the attendance file: ")
    try:
        result = run(file_path)
        print(result.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")
