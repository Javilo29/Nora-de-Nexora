import time
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        # Estructura: { 'cliente_id': { 'historial': [], 'last_active': timestamp } }
        self.tenants = {}

    def get_tenant_memory(self, cliente_id):
        """Retorna el historial de un cliente específico, creándolo si no existe."""
        if cliente_id not in self.tenants:
            self.tenants[cliente_id] = {
                'historial': [],
                'last_active': time.time()
            }
        
        # Actualizar tiempo de actividad
        self.tenants[cliente_id]['last_active'] = time.time()
        return self.tenants[cliente_id]['historial']

    def add_message(self, cliente_id, role, content):
        """Agrega un mensaje al historial del cliente."""
        history = self.get_tenant_memory(cliente_id)
        history.append({"role": role, "content": content})
        
        # Limitar a los últimos 15 mensajes para mantener contexto relevante y bajo costo
        if len(history) > 15:
            history.pop(0)

    def limpiar_memoria_antigua(self):
        """Elimina tenants inactivos por más de 60 minutos."""
        ahora = time.time()
        limite = 60 * 60  # 1 hora
        to_delete = []
        
        for cid, data in self.tenants.items():
            if ahora - data['last_active'] > limite:
                to_delete.append(cid)
        
        for cid in to_delete:
            del self.tenants[cid]
            logger.info(f"Memoria del cliente {cid} liberada por inactividad.")
        
        return len(to_delete)
