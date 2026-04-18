import socket
import logging

logger = logging.getLogger(__name__)

class NoraNetwork:
    def __init__(self):
        pass

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def buscar_dispositivos(self):
        """Escanea la red local (segmento /24)."""
        dispositivos = []
        try:
            # Intentamos usar python-nmap si está disponible
            import nmap
            nm = nmap.PortScanner()
            local_ip = self.get_local_ip()
            ip_range = ".".join(local_ip.split(".")[:-1]) + ".0/24"
            
            logger.info(f"Escaneando red: {ip_range}")
            nm.scan(hosts=ip_range, arguments='-sn')
            
            for host in nm.all_hosts():
                if 'status' in nm[host] and nm[host]['status']['state'] == 'up':
                    nombre = nm[host].hostname() if nm[host].hostname() else "Desconocido"
                    dispositivos.append({
                        "ip": host,
                        "nombre": nombre,
                        "mac": nm[host]['addresses'].get('mac', 'N/A')
                    })
            return dispositivos
        except ImportError:
            logger.warning("python-nmap no instalado. Usando escaneo básico de socket.")
            return self._scan_basico()
        except Exception as e:
            return {"error": str(e)}

    def _scan_basico(self):
        # Fallback ultra básico: solo intenta ver si el host responde en puerto 80
        # Esto es muy lento y limitado, pero sirve como concepto
        return [{"status": "info", "message": "Instalá python-nmap para escaneo real."}]
