import os
import logging

logger = logging.getLogger(__name__)

class NoraMemory:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        
        # Fallback memory in RAM: {user_id: [messages]}
        self.local_history = {}
        
        if self.use_supabase:
            try:
                from supabase import create_client
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info("Memoria conectada a Supabase.")
            except ImportError:
                logger.warning("Librería 'supabase' no encontrada. Usando RAM.")
                self.use_supabase = False

    def add_message(self, user_id, role, content):
        """Guarda un mensaje en el historial."""
        if self.use_supabase:
            try:
                data = {
                    "user_id": str(user_id),
                    "role": role,
                    "content": content
                }
                self.supabase.table("chat_history").insert(data).execute()
            except Exception as e:
                logger.error(f"Error guardando en Supabase: {e}")
                self._add_to_local(user_id, role, content)
        else:
            self._add_to_local(user_id, role, content)

    def _add_to_local(self, user_id, role, content):
        if user_id not in self.local_history:
            self.local_history[user_id] = []
        self.local_history[user_id].append({"role": role, "content": content})
        # Mantener solo los últimos 20 mensajes en RAM
        if len(self.local_history[user_id]) > 20:
            self.local_history[user_id].pop(0)

    def get_history(self, user_id, limit=10):
        """Recupera el historial reciente."""
        if self.use_supabase:
            try:
                response = self.supabase.table("chat_history") \
                    .select("*") \
                    .eq("user_id", str(user_id)) \
                    .order("id", desc=True) \
                    .limit(limit) \
                    .execute()
                # Voltear para que sea cronológico
                return [{"role": m["role"], "content": m["content"]} for m in reversed(response.data)]
            except Exception as e:
                logger.error(f"Error leyendo de Supabase: {e}")
                return self.local_history.get(user_id, [])
        else:
            return self.local_history.get(user_id, [])[-limit:]
