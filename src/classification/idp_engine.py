import sqlite3
import os
import json

DB_PATH = r"D:\AGENTE_IA\data\db\system.db"
VAULT_PATH = r"D:\AGENTE_IA\data\vault"

def get_pending_documents():
    """Generador para obtener documentos pendientes de clasificar uno a uno."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, client_id, filename, file_path FROM documents WHERE status = 'received'")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row
    conn.close()

def classify_document(doc_id, client_id, filename, file_path):
    """
    Simula la clasificación de un documento.
    Mueve el archivo al directorio final correspondiente.
    """
    print(f"Clasificando: {filename} (ID: {doc_id})")
    
    # Lógica de clasificación simplificada (por nombre o metadatos)
    category = "invoices" if "factura" in filename.lower() else "statements"
    
    # Ruta destino final
    dest_dir = os.path.join(VAULT_PATH, f"CU-001", category) # Usamos CU-001 por simplicidad de la prueba
    os.makedirs(dest_dir, exist_ok=True)
    
    dest_path = os.path.join(dest_dir, filename)
    
    # Simular movimiento de archivo (en producción sería shutil.move)
    print(f"Moviendo {file_path} -> {dest_path}")
    
    # Actualizar DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE documents 
        SET status = 'processed', category = ?, file_path = ?
        WHERE id = ?
    ''', (category, dest_path, doc_id))
    conn.commit()
    conn.close()
    
    print(f"Documento {filename} clasificado exitosamente como {category}.")

def run_classifier():
    print("Iniciando motor de clasificación IDP...")
    for doc in get_pending_documents():
        classify_document(*doc)
    print("Clasificación completada.")

if __name__ == "__main__":
    run_classifier()
