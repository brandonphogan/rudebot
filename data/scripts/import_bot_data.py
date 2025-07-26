import sqlite3
import json
import os

# Database and import paths (updated for new data directory structure)
DB_PATH = 'data/rudebot.sqlite3'
IMPORT_PATH = 'data/bot_data.json'

def import_all():
    if not os.path.exists(IMPORT_PATH):
        print(f"File not found: {IMPORT_PATH}")
        return
    
    with open(IMPORT_PATH, 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Track what was actually imported vs what already existed
    imported_counts = {'command_types': 0, 'action_types': 0, 'responses': 0}
    existing_counts = {'command_types': 0, 'action_types': 0, 'responses': 0}
    
    # Import command_types
    for ct in data.get('command_types', []):
        cursor.execute("SELECT 1 FROM command_types WHERE command_type = ?", (ct['command_type'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO command_types (command_type) VALUES (?)", (ct['command_type'],))
            imported_counts['command_types'] += 1
        else:
            existing_counts['command_types'] += 1
    
    # Import action_types
    for at in data.get('action_types', []):
        cursor.execute("SELECT 1 FROM action_types WHERE action_type = ?", (at['action_type'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO action_types (action_type, description) VALUES (?, ?)", (at['action_type'], at.get('description')))
            imported_counts['action_types'] += 1
        else:
            existing_counts['action_types'] += 1
    
    # Import responses - use category + trigger as unique identifier
    for resp in data.get('responses', []):
        # Check if a response with this category and trigger already exists
        cursor.execute("SELECT id FROM responses WHERE category = ? AND trigger = ?", (
            resp.get('category'), resp.get('trigger')))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing response with new data
            cursor.execute("""
                UPDATE responses 
                SET text = ?, gif_url = ?, emote = ?, action = ?
                WHERE id = ?
            """, (
                resp.get('text'), resp.get('gif_url'), resp.get('emote'), resp.get('action'), existing[0]
            ))
            existing_counts['responses'] += 1
        else:
            # Insert new response
            cursor.execute("""
                INSERT INTO responses (category, trigger, text, gif_url, emote, action) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                resp.get('category'), resp.get('trigger'), resp.get('text'), 
                resp.get('gif_url'), resp.get('emote'), resp.get('action')
            ))
            imported_counts['responses'] += 1
    
    conn.commit()
    
    # Print detailed import summary
    print("Database import summary:")
    print(f"  Command types: {imported_counts['command_types']} imported, {existing_counts['command_types']} already existed")
    print(f"  Action types: {imported_counts['action_types']} imported, {existing_counts['action_types']} already existed")
    print(f"  Responses: {imported_counts['responses']} imported, {existing_counts['responses']} updated")
    
    conn.close()

if __name__ == '__main__':
    import_all() 