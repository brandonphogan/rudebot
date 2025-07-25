import sqlite3
import json
import os

DB_PATH = 'db/rudebot.sqlite3'
IMPORT_PATH = 'data/bot_data.json'

def import_all():
    if not os.path.exists(IMPORT_PATH):
        print(f"File not found: {IMPORT_PATH}")
        return
    with open(IMPORT_PATH, 'r') as f:
        data = json.load(f)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Import command_types
    for ct in data.get('command_types', []):
        cursor.execute("SELECT 1 FROM command_types WHERE command_type = ?", (ct['command_type'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO command_types (command_type) VALUES (?)", (ct['command_type'],))
    # Import action_types
    for at in data.get('action_types', []):
        cursor.execute("SELECT 1 FROM action_types WHERE action_type = ?", (at['action_type'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO action_types (action_type, description) VALUES (?, ?)", (at['action_type'], at.get('description')))
    # Import responses
    for resp in data.get('responses', []):
        cursor.execute("SELECT 1 FROM responses WHERE category = ? AND trigger = ? AND text = ? AND gif_url = ? AND emote = ? AND action = ?", (
            resp.get('category'), resp.get('trigger'), resp.get('text'), resp.get('gif_url'), resp.get('emote'), resp.get('action')))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO responses (category, trigger, text, gif_url, emote, action) VALUES (?, ?, ?, ?, ?, ?)", (
                resp.get('category'), resp.get('trigger'), resp.get('text'), resp.get('gif_url'), resp.get('emote'), resp.get('action')))
    conn.commit()
    print(f"Imported {len(data.get('command_types', []))} command types, {len(data.get('action_types', []))} action types, and {len(data.get('responses', []))} responses.")
    conn.close()

if __name__ == '__main__':
    import_all() 