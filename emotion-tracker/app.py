from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import calendar

app = Flask(__name__)

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

def get_notes_for_date(date):
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT emotion, note, id  -- Ensure id is being selected
        FROM emotions 
        WHERE DATE(timestamp) = ?
    ''', (date,))
    notes = cursor.fetchall()
    conn.close()
    return notes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/note-feelings')
def note_feelings():
    emotion = request.args.get('emotion', '')
    return render_template('note-feelings.html', emotion=emotion)

@app.route('/submit', methods=['POST'])
def submit_feeling():
    emotion = request.form['feeling']
    note = request.form['note']
    
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO emotions (emotion, note) VALUES (?, ?)', (emotion, note))
    conn.commit()
    conn.close()
    
    return redirect(url_for('thank_you'))


@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')


@app.route('/view-notes/<timestamp>', methods=['GET'])
def view_notes(timestamp):

    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, emotion, note FROM emotions WHERE timestamp = ?', (timestamp,))
    notes = cursor.fetchall()
    conn.close()

    return render_template('view-notes.html', timestamp=timestamp, notes=notes)

@app.route('/view-notes-by-date/<date>', methods=['GET'])
def view_notes_by_date(date):
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, emotion, note 
        FROM emotions 
        WHERE DATE(timestamp) = ?
    ''', (date,))
    notes = cursor.fetchall()
    conn.close()

    return render_template('view-notes.html', date=date, notes=notes)

@app.route('/delete-note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM emotions WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_emotions'))




@app.route('/view')
def view_emotions():
    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    

    cursor.execute('SELECT timestamp, emotion FROM emotions ORDER BY timestamp ASC')
    emotions_data = cursor.fetchall()
    conn.close()

    timestamps = [record[0] for record in emotions_data]  
    emotions = []
    
    emotion_map = {
        'angry': 1,
        'sad': 2,
        'neutral': 3,
        'happy': 4,
        'excited': 5
    }

    for record in emotions_data:
        emotion_text = record[1].lower()  
        emotion_value = emotion_map.get(emotion_text, 3) 
        emotions.append(emotion_value)

    return render_template('view-emotions.html', dates=timestamps, emotions=emotions)

@app.route('/calendar-view', methods=['GET', 'POST'])
def calendar_view():

    selected_month = request.args.get('month', None)
    selected_year = request.args.get('year', None)

    if not selected_month or not selected_year:
        today = datetime.today()
        selected_month = today.strftime('%m')
        selected_year = today.strftime('%Y')

    selected_month_int = int(selected_month)
    selected_year_int = int(selected_year)

    conn = sqlite3.connect('emotions.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(timestamp) as date, emotion FROM emotions
        WHERE strftime('%m', timestamp) = ? AND strftime('%Y', timestamp) = ?
    ''', (selected_month, selected_year))
    notes = cursor.fetchall()
    conn.close()

    calendar_data = {}
    for date, emotion in notes:
        calendar_data[date] = emotion

    num_days = calendar.monthrange(selected_year_int, selected_month_int)[1]

    emotion_colors = {
        'happy': '#FFD700',  
        'excited': '#FF4500',
        'angry': '#FF0000',  
        'sad': '#1E90FF',     
        'calm': '#32CD32'    
    }

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


