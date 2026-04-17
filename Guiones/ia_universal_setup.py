# Proyecto: Nora de Nexora - MyJNexoraVisual
import os
import shutil
import psutil
from pathlib import Path

def get_disk_info():
    """Detecta discos y espacio disponible."""
    print("🔍 Analizando hardware de almacenamiento...")
    disks = psutil.disk_partitions()
    recommendations = []
    
    for disk in disks:
        try:
            usage = psutil.disk_usage(disk.mountpoint)
            free_gb = usage.free / (1024**3)
            # Intentamos detectar si es SSD o HDD (basado en el nombre o simple heurística de tamaño/letra)
            is_ssd = "C:" in disk.mountpoint # Heurística común para OS
            
            recommendations.append({
                "mount": disk.mountpoint,
                "free": free_gb,
                "is_likely_ssd": is_ssd
            })
            print(f"📍 Unidad {disk.mountpoint} | Libre: {free_gb:.2f} GB | {'SSD (Sugerido para App)' if is_ssd else 'HDD (Sugerido para Datos)'}")
        except:
            continue
    return recommendations

def setup_universal(target_drive=None):
    if not target_drive:
        info = get_disk_info()
        # Elegimos D: si existe, sino C:
        target_drive = "D:" if any(d['mount'] == "D:\\" for d in info) else "C:"
    
    install_path = Path(f"{target_drive}\\NORA_AI_UNIVERSAL")
    print(f"\n🚀 Instalando Nora en: {install_path}")
    
    # Crear estructura
    folders = ["Scripts", "Knowledge", "Assets", "Reportes", "Inbox", "data/db", "LOGS", "tmp"]
    for folder in folders:
        (install_path / folder).mkdir(parents=True, exist_ok=True)
    
    # Crear archivo .env base
    env_content = "GEMINI_API_KEY=PEGUE_AQUI\nSUPABASE_URL=URL_AQUI\nWORK_MODE=Contabilidad\n"
    with (install_path / ".env").open("w") as f:
        f.write(env_content)
    
    print(f"✅ Instalación 'Drive-Agnostic' completada en {target_drive}.")
    return install_path

if __name__ == "__main__":
    setup_universal()
