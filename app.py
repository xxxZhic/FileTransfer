from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, flash
import os
import json

app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for flashing messages

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    print(f"Created upload directory at {app.config['UPLOAD_FOLDER']}")

# Load messages
if os.path.exists('messages.json'):
    with open('messages.json', 'r') as f:
        messages = json.load(f)
else:
    messages = {}

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files, messages=messages)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        print(f"Saving file to {file_path}")  # Debug output
        file.save(file_path)
        if os.path.exists(file_path):
            print(f"File saved successfully: {file_path}")
        else:
            print(f"File not saved: {file_path}")
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Function to load messages from a JSON file
def load_messages():
    if os.path.exists('messages.json'):
        with open('messages.json', 'r') as file:
            return json.load(file)
    return {}
messages = load_messages()

# Function to save messages to a JSON file
def save_messages(messages):
    with open('messages.json', 'w') as file:
        json.dump(messages, file, indent=4)

@app.route('/upload_message', methods=['POST'])
@app.route('/upload_message', methods=['POST'])
def upload_message():
    username = request.form['username']
    message = request.form['message']

    # Ensure that the messages dictionary stores a list for each user
    if username in messages:
        # If the username already exists, append the message to the existing list
        if isinstance(messages[username], list):
            messages[username].append(message)
        else:
            messages[username] = [messages[username], message]
    else:
        # If the username doesn't exist, create a new list with the message
        messages[username] = [message]

    save_messages(messages)

    return redirect('/')


@app.route('/delete_message/<username>/<int:index>', methods=['POST'])
def delete_message(username, index):
    if username in messages and len(messages[username]) > index:
        del messages[username][index]
        if not messages[username]:  # Remove user if no messages left
            del messages[username]
        
        # Save the updated messages
        save_messages(messages)
        
    return redirect('/')



@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))



@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    
    # Search for matching files
    matching_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if query in f.lower()]

    # Search for matching messages
    matching_messages = {}
    for user, msgs in messages.items():
        if query in user.lower():
            matching_messages[user] = msgs
        else:
            # Check within each message string
            filtered_msgs = [msg for msg in msgs if query in msg.lower()]
            if filtered_msgs:
                matching_messages[user] = filtered_msgs

    return jsonify({'files': matching_files, 'messages': matching_messages})



if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True, port= 5001)
