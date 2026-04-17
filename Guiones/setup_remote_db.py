import os
import pg8000.native
from dotenv import load_dotenv
import re

# Cargando variables de entorno
load_dotenv(dotenv_path=r"D:\AGENTE_IA\.env")

def setup_remote():
    url = os.getenv("SUPABASE_URL")
    password = os.getenv("DB_PASSWORD")
    
    if not url or not password or "tu-proyecto" in url:
        print("Error: Credenciales incompletas en .env (Se requiere SUPABASE_URL y DB_PASSWORD)")
        return

    # Extraer el host de la URL: https://[REF].supabase.co -> db.[REF].supabase.co
    project_ref = re.search(r"https://(.*?)\.supabase\.co", url)
    if not project_ref:
        print("Error: Formato de SUPABASE_URL inválido.")
        return
    
    host = f"db.{project_ref.group(1)}.supabase.co"
    user = "postgres"
    database = "postgres"
    port = 5432

    print(f"Iniciando migración en: {host}...")

    try:
        # Leer archivo SQL
        sql_file_path = r"D:\AGENTE_IA\Scripts\supabase_schema.sql"
        if not os.path.exists(sql_file_path):
            print(f"Error: No se encuentra el archivo {sql_file_path}")
            return
            
        with open(sql_file_path, "r", encoding="utf-8") as f:
            full_sql = f.read()

        # Separar por punto y coma y filtrar vacíos
        commands = [cmd.strip() for cmd in full_sql.split(";") if cmd.strip()]

        con = pg8000.native.Connection(
            user=user,
            host=host,
            database=database,
            port=port,
            password=password
        )

        for cmd in commands:
            try:
                con.run(cmd)
                # Extraer nombre de tabla para el log
                match = re.search(r"TABLE IF NOT EXISTS (ia_.*?) \(", cmd)
                if match:
                    print(f"Tabla {match.group(1)}: OK")
            except Exception as sql_err:
                print(f"Aviso en comando: {sql_err}")

        con.close()
        print("\nMigración/Actualización finalizada. Liberando RAM.")

    except Exception as e:
        print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    setup_remote()
