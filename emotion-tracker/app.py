from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import calendar

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emotion TEXT NOT NULL,
            note TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Function to get notes for a specific date
def get_notes_for_date(date):
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT emotion, note 
        FROM emotions 
        WHERE DATE(timestamp) = ?
    ''', (date,))
    notes = cursor.fetchall()
    conn.close()
    return notes

# Route for the main page (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Route for the note-feelings form (note-feelings.html)
@app.route('/note-feelings')
def note_feelings():
    emotion = request.args.get('emotion', '')
    return render_template('note-feelings.html', emotion=emotion)

# Route to handle the form submission
@app.route('/submit', methods=['POST'])
def submit_feeling():
    emotion = request.form['feeling']
    note = request.form['note']
    
    # Insert the form data into the database
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO emotions (emotion, note) VALUES (?, ?)', (emotion, note))
    conn.commit()
    conn.close()
    
    # After submitting the form, redirect to the thank you page
    return redirect(url_for('thank_you'))

# Route to show the thank you page
@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')


@app.route('/view-notes/<timestamp>', methods=['GET'])
def view_notes(timestamp):
    # Query your database for the note corresponding to the exact timestamp
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()

    # Select emotion and note for the provided exact timestamp
    cursor.execute('SELECT emotion, note FROM emotions WHERE timestamp = ?', (timestamp,))
    notes = cursor.fetchall()
    conn.close()

    # Render the notes on the view_notes.html page
    return render_template('view-notes.html', timestamp=timestamp, notes=notes)

@app.route('/view-notes-by-date/<date>', methods=['GET'])
def view_notes_by_date(date):
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()

    # Select emotion and note for the provided date (matching only the date part)
    cursor.execute('''
        SELECT emotion, note 
        FROM emotions 
        WHERE DATE(timestamp) = ?
    ''', (date,))
    notes = cursor.fetchall()
    conn.close()

    return render_template('view-notes.html', date=date, notes=notes)


@app.route('/view')
def view_emotions():
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    
    # Retrieve full timestamps (including time) from the database
    cursor.execute('SELECT timestamp, emotion FROM emotions ORDER BY timestamp ASC')
    emotions_data = cursor.fetchall()
    conn.close()

    # Extract full timestamps and emotions from the database records
    timestamps = [record[0] for record in emotions_data]  # Keep full timestamp (YYYY-MM-DD HH:MM:SS)
    emotions = []
    
    # Map emotion text to a numerical value for the chart
    emotion_map = {
        'angry': 1,
        'sad': 2,
        'neutral': 3,
        'happy': 4,
        'excited': 5
    }

    for record in emotions_data:
        emotion_text = record[1].lower()  # Convert emotion to lowercase to match the map
        emotion_value = emotion_map.get(emotion_text, 3)  # Default to 'neutral' if not found
        emotions.append(emotion_value)

    # Pass full timestamps and emotions to the view-emotions.html template
    return render_template('view-emotions.html', dates=timestamps, emotions=emotions)


# Change the route and function name from 'calendar' to something like 'calendar_view'
@app.route('/calendar-view', methods=['GET', 'POST'])
def calendar_view():
    # Get the selected month and year from the form
    selected_month = request.args.get('month', None)
    selected_year = request.args.get('year', None)

    # Default to the current month and year if not provided
    if not selected_month or not selected_year:
        today = datetime.today()
        selected_month = today.strftime('%m')
        selected_year = today.strftime('%Y')

    # Convert selected month and year to integers for further processing
    selected_month_int = int(selected_month)
    selected_year_int = int(selected_year)

    # Retrieve all notes from the database for the selected month and year
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(timestamp) as date, emotion FROM emotions
        WHERE strftime('%m', timestamp) = ? AND strftime('%Y', timestamp) = ?
    ''', (selected_month, selected_year))
    notes = cursor.fetchall()
    conn.close()

    # Prepare a dictionary to hold the colors for each date
    calendar_data = {}
    for date, emotion in notes:
        calendar_data[date] = emotion

    # Get the number of days in the selected month
    num_days = calendar.monthrange(selected_year_int, selected_month_int)[1]

    # Define emotion to color mapping
    emotion_colors = {
        'happy': '#FFD700',   # Gold
        'excited': '#FF4500', # OrangeRed
        'angry': '#FF0000',   # Red
        'sad': '#1E90FF',     # DodgerBlue
        'calm': '#32CD32'     # LimeGreen
    }

    # Define emotion to emoji mapping
    emotion_emojis = {
        'happy': '😊',
        'excited': '🏎',
        'angry': '😡',
        'sad': '😢',
        'calm': '😌',
    }

    return render_template('calendar.html', 
                           calendar_data=calendar_data, 
                           emotion_colors=emotion_colors, 
                           emotion_emojis=emotion_emojis,
                           selected_month=selected_month, 
                           selected_year=selected_year,
                           num_days=num_days)



if __name__ == '__main__':
    init_db() 
    app.run(debug=True)


