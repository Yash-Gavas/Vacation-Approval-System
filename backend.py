# backend.py
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')

# Simulated data storage
meetings_schedule = {'2024-02-10', '2024-02-15'}  # Dates with scheduled meetings
special_events = {'2024-02-20'}  # Dates with special events
project_submission_date = '2024-02-25'  # Example project submission date

def get_schedule_info(date):
    # Replace this with your actual data source or logic to retrieve schedule information
    schedule_data = {
        '2024-02-25': 'Team meeting',
        '2024-02-20': 'Company anniversary',
        '2024-02-15': 'Project submission',
        # Add more entries as needed
    }

    # Get the schedule information for the given date, or a default message if not found
    return schedule_data.get(date, 'Scheduled event')

def find_nearby_free_dates(busy_date):
    busy_date_obj = datetime.strptime(busy_date, "%Y-%m-%d")

    # Find dates before and after the busy date
    nearby_free_dates = []
    previous_dates = [busy_date_obj - timedelta(days=i) for i in range(1, 6)]
    next_dates = [busy_date_obj + timedelta(days=i) for i in range(1, 6)]

    for date in previous_dates + [busy_date_obj] + next_dates:
        date_str = date.strftime("%Y-%m-%d")
        if date_str not in meetings_schedule and date_str not in special_events and date_str != project_submission_date:
            nearby_free_dates.append(date_str)

    if not nearby_free_dates:
        return None, "No nearby free dates available.", None

    return nearby_free_dates, None, None


# Home route
@app.route('/')
def index():
    return render_template('templatesindex.html')

# Vacation request approval route
@app.route('/approve_request', methods=['POST'])
def approve_request():
    try:
        employee_id = request.form['employeeId']
        department = request.form['department']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']

        # Check for missing fields
        if not employee_id or not department or not start_date or not end_date or not reason:
            return render_template('templatesindex.html', result="Please fill in all fields.")

        # Convert start_date and end_date to datetime objects
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        # Check for conflicts with all scheduled dates (meetings, special events, project submission)
        all_conflicts = [date for date in meetings_schedule | special_events | {project_submission_date} if start_date_obj <= datetime.strptime(date, "%Y-%m-%d") <= end_date_obj]

        # Check if there are any conflicts
        if all_conflicts:
            denial_reason = f"Leave request for {employee_id} denied due to scheduled events on the following dates:"

            # Include specific information for all conflicts
            for conflict_date in all_conflicts:
                schedule_info = get_schedule_info(conflict_date)
                denial_reason += f"\n- {conflict_date}: {schedule_info}."

            # Find nearby free dates
            nearby_free_dates, nearby_free_dates_info, nearby_free_dates_error = find_nearby_free_dates(start_date)

            # Modify the return statement to include the specific denial reason
            return render_template('denied.html', result=denial_reason, denied=True, denial_reason=denial_reason, nearby_free_dates=nearby_free_dates, nearby_free_dates_info=nearby_free_dates_info, nearby_free_dates_error=nearby_free_dates_error)


        # All checks passed, approve the leave
        result_message = f"Leave request for {employee_id} approved. Start Date: {start_date}, End Date: {end_date}, Reason: {reason}"

        # Add this line to trigger the popup message
        return render_template('approved.html', result=result_message, show_popup=True)
    except KeyError:
        return render_template('templatesindex.html', result="Error: Employee data not found in the form.")

if __name__ == '__main__':
    app.run(debug=True)
