import sqlite3
import json

# Database and export paths (updated for new data directory structure)
DB_PATH = 'data/rudebot.sqlite3'
EXPORT_PATH = 'data/bot_data.json'

def export_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    def export_table(table):
        cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    data = {
        'responses': export_table('responses'),
        'command_types': export_table('command_types'),
        'action_types': export_table('action_types'),
    }

    with open(EXPORT_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Exported bot data to {EXPORT_PATH}")
    conn.close()

if __name__ == '__main__':
    export_all() 