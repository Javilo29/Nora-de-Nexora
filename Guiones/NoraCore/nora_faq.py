# Diccionario de Conocimiento de Negocio de Nexora Visual

FAQ = {
    "¿qué servicios ofrecen?": "En Nexora Visual ofrecemos soluciones de IA para automatización administrativa y comercial. Ayudamos a las empresas a ser más eficientes mediante agentes inteligentes. ¿Le gustaría agendar una demo con nuestro equipo?",
    "¿quiénes son?": "Somos Nexora Visual, líderes en la integración de Inteligencia Artificial para el sector corporativo. Transformamos procesos manuales en flujos de trabajo autónomos.",
    "¿cómo contacto con soporte?": "Puede contactar con nuestro equipo técnico enviando un correo a soporte@nexora.com.ar o a través de este mismo canal si es cliente premium.",
    "¿qué es nora?": "Nora es nuestra agente de IA avanzada, diseñada para gestionar tareas administrativas, analizar facturas y asistir en la toma de decisiones empresariales.",
    "¿cuánto cuesta?": "Nuestros planes son personalizados según el volumen de operaciones de su empresa. Si gusta, puedo derivar su consulta al departamento comercial."
}

def buscar_en_faq(query):
    """Búsqueda simple de coincidencias en el FAQ."""
    q = query.lower().strip()
    # Buscamos coincidencias de palabras clave o similitud simple
    for pregunta, respuesta in FAQ.items():
        if pregunta in q or q in pregunta:
            return respuesta
    return None
