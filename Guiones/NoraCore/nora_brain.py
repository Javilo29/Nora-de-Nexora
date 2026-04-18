import os
import logging
from groq import Groq
from .nora_memory_manager import MemoryManager
from .nora_faq import buscar_en_faq

logger = logging.getLogger(__name__)

class NoraBrain:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.memory = MemoryManager()
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        
        # Filtro de respuestas locales para ahorrar tokens
        self.STOP_WORDS_RESPONSES = {
            "gracias": "Es un placer asistirle. En Nexora Visual estamos a un mensaje de distancia.",
            "chau": "Hasta luego. Recuerde que Nora está aquí para optimizar su gestión administrativa.",
            "adiós": "Que tenga un excelente día. Saludos de parte del equipo de Nexora Visual.",
            "ok": "Entendido. ¿Hay algo más en lo que pueda asistirle?",
            "bueno": "Perfecto. Quedo a su disposición."
        }
        
        self.NORA_SYSTEM_PROMPT = """
Eres Nora, la Asistente Virtual Oficial de Nexora Visual. Tu tono es profesional, ejecutivo, pero amable. 
Hablas español neutro (evitá modismos argentinos extremos para clientes internacionales, pero mantené calidez). 
Tu objetivo es asistir en la gestión de facturas, recordatorios y consultas administrativas. 
No inventes información. Si no sabes algo, dices: 'Permítame consultarlo con el equipo de Nexora Visual'. 
Siempre te identificas como parte de Nexora Visual.
"""

    def get_response(self, user_id, user_text, is_admin=False):
        # 1. Limpieza de memoria (mantenimiento)
        self.memory.limpiar_memoria_antigua()
        
        user_text_lower = user_text.lower().strip()

        # 2. Filtro de Intención Local (Ahorro de Tokens)
        if user_text_lower in self.STOP_WORDS_RESPONSES:
            return self.STOP_WORDS_RESPONSES[user_text_lower]

        # 3. Consulta al FAQ de Negocio
        faq_response = buscar_en_faq(user_text_lower)
        if faq_response:
            return faq_response

        # 4. Procesamiento con IA (Groq)
        history = self.memory.get_tenant_memory(user_id)
        
        messages = [{"role": "system", "content": self.NORA_SYSTEM_PROMPT}]
        if is_admin:
            messages[0]["content"] += "\n[MODO ADMIN ACTIVADO]"
            
        for msg in history:
            messages.append(msg)
            
        messages.append({"role": "user", "content": user_text})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5, # Bajamos temperatura para más consistencia profesional
                max_tokens=800
            )
            
            response_text = completion.choices[0].message.content
            
            # Guardar en memoria aislada
            self.memory.add_message(user_id, "user", user_text)
            self.memory.add_message(user_id, "assistant", response_text)
            
            return response_text
        except Exception as e:
            logger.error(f"Error en NoraBrain: {e}")
            return "Lo lamento, he tenido un inconveniente técnico. Permítame consultarlo con el equipo de Nexora Visual."
