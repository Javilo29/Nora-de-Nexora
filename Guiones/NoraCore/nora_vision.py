import os
import base64
import json
from io import BytesIO
from PIL import Image
from groq import Groq

class NoraVision:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def encode_image(self, img_bytesio):
        img_bytesio.seek(0)
        return base64.b64encode(img_bytesio.read()).decode('utf-8')

    def optimizar_imagen(self, img_bytesio, max_size=1024):
        img_bytesio.seek(0)
        img = Image.open(img_bytesio)
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return output

    def analizar_factura(self, img_bytesio):
        """Analiza una factura y extrae datos clave."""
        try:
            img_opt = self.optimizar_imagen(img_bytesio)
            img_b64 = self.encode_image(img_opt)
            
            prompt = """
Analizá esta imagen de factura.
Devolvé UNICAMENTE un JSON válido:
{"cuit": "xx-xxxxxxxx-x", "importe": numero, "fecha": "dd/mm/aaaa", "tipo": "factura/ticket/otro"}
"""
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]}
                ]
            )
            return json.loads(completion.choices[0].message.content.strip())
        except Exception as e:
            return {"error": str(e)}

    def analizar_rostro(self, img_bytesio):
        """Detecta si el rostro coincide con el Administrador (Javi)."""
        # Nota: Requiere face_recognition. Si no está, devolvemos False por seguridad.
        try:
            import face_recognition
            import numpy as np
            
            # Cargar referencia del admin (debe existir Activos/javi_face.jpg)
            ref_path = "Activos/javi_face.jpg"
            if not os.path.exists(ref_path):
                return {"status": "error", "message": "No hay referencia facial del admin."}
                
            img_bytesio.seek(0)
            img_actual = face_recognition.load_image_file(img_bytesio)
            face_encodings = face_recognition.face_encodings(img_actual)
            
            if not face_encodings:
                return {"status": "no_face", "message": "No se detectó ningún rostro."}
                
            img_admin = face_recognition.load_image_file(ref_path)
            admin_encoding = face_recognition.face_encodings(img_admin)[0]
            
            # Comparar (tolerancia 0.6 por defecto)
            results = face_recognition.compare_faces([admin_encoding], face_encodings[0])
            
            if results[0]:
                return {"status": "success", "admin": "Javi"}
            else:
                return {"status": "denied", "message": "Rostro no reconocido."}
                
        except ImportError:
            return {"status": "error", "message": "Módulo face_recognition no instalado."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
