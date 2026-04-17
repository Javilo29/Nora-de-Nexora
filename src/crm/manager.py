import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = r"D:\AGENTE_IA\data\db\system.db"

def add_task(client_id, title, description, days_to_due=7, priority='medium'):
    """Registra una nueva tarea/vencimiento para un cliente."""
    due_date = (datetime.now() + timedelta(days=days_to_due)).strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (client_id, title, description, due_date, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', (client_id, title, description, due_date, priority))
    conn.commit()
    conn.close()
    print(f"Tarea '{title}' registrada para el cliente {client_id}. Vence: {due_date}")

def get_upcoming_tasks():
    """Genera reportes de tareas próximas a vencer."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.name, t.title, t.due_date, t.priority 
        FROM tasks t
        JOIN clients c ON t.client_id = c.id
        WHERE t.status = 'pending'
        ORDER BY t.due_date ASC
    ''')
    
    tasks = cursor.fetchall()
    conn.close()
    return tasks

if __name__ == "__main__":
    print("Módulo de Gestión CRM/RPM Iniciado.")
    # Ejemplo de uso: Crear una tarea de prueba
    add_task(1, "Presentación IVA Trimestral", "Revisión de facturas del mes", 15, 'high')
    
    print("\nPróximos Vencimientos:")
    for task in get_upcoming_tasks():
        print(f"[{task[2]}] {task[0]}: {task[1]} (Prioridad: {task[3]})")
