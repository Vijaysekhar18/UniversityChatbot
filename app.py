import os
import signal
from flask import Flask, render_template, request, jsonify
import json
import re
import smtplib
import ssl
import sqlite3
from chat import get_response

app = Flask(__name__)
app.config['TEMPLATES'] = 'templates'
app.template_folder = 'templates'

# Initialize the conversation JSON file
CONVERSATION_FILE = 'conversation.json'

######

conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               email TEXT NOT NULL
               )''')
conn.commit()
conn = sqlite3.connect('conversation.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS conversation (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               email TEXT NOT NULL,
               question TEXT NOT NULL,
               answer TEXT NOT NULL
               )''')
conn.commit()
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn
######
@app.route('/')
def form():
    return render_template("form.html")

@app.route('/chatbot', methods=['post'])
def save_data():
    name = request.form.get('name')
    print(name)
    email_ID = request.form.get('email')
    print(email_ID)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email_ID))
    conn.commit()
    cur.execute("SELECT * FROM users")

# Fetch all rows from the cursor
    rows = cur.fetchall()
    for row in rows:
# Print the fetched rows
        for value in row:
            print(value)
    cur.close()
    conn.close()
       
    return render_template("base.html")

@app.post('/predict')
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    
    ####
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM users ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    user_email = row[0] if row else None
    # Insert the conversation into the database
    conn = sqlite3.connect('conversation.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO conversation (email, question, answer) VALUES (?, ?, ?)", (user_email, text, response))
    conn.commit()
    print("::::::_____success--------::::::")
    ###

    # Append the conversation to the JSON file
    append_to_conversation(text, response)
    
    # Return the response with URLs replaced
    return jsonify({"answer": response})



@app.route('/sendEmail', methods=['POST'])
def send_email():
    # Get the user's email from the request
    print("---------Give me a moment I am trying to send you a mail----------------")
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM users ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    user_email = row[0] if row else None
    print("Hello I am here")

    # Fetch chat history for the user's email
    conn = sqlite3.connect('conversation.db')
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM conversation WHERE email=?", (user_email,))
    rows = cur.fetchall()
    chat_history = ""
    for row in rows:
        chat_history += f"User: {row[0]}\nChatbot: {row[1]}\n\n"

    # Email configuration
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server
    email_from = "saiputta730660@gmail.com"
    pswd = "bvgkinfiuiekjupm"  # Update this with your actual password
    message = f"Here is your chat history:\n\n{chat_history}\n\nPlease provide your feedback by replying to this email."

    # Create context
    simple_email_context = ssl.create_default_context()

    try:
        # Connect to the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, pswd)
        print("Connected to server :-)")
    
        # Send the email
        print(f"Sending email to - {user_email}")
        TIE_server.sendmail(email_from, user_email, message)
        print(f"Email successfully sent to - {user_email}")

    except Exception as e:
        print(e)

    finally:
        TIE_server.quit()
        os.kill(os.getpid(), signal.SIGINT)


    return jsonify({"success": True})
#####

def append_to_conversation(question, answer):
    conversation = {"question": question, "answer": answer}
    with open(CONVERSATION_FILE, 'a') as file:
        # Serialize the conversation data to JSON with proper indentation
        json.dump(conversation, file, indent=4)
        file.write('\n')  # Add a newline to separate conversations



if __name__ == "__main__":
    app.run(debug=True)
