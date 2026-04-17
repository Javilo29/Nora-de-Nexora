# -*- coding: utf-8 -*-
# Nora de Nexora v5.4 — persistencia local multirrubro (SQLite)
import os
import sqlite3
from pathlib import Path
from typing import Any

from ia_paths import LOCAL_DB_FILE

# Metadatos de respuesta: terminología universal (no exclusiva de salud)
METADATA_ENTITY_LABEL = "Clientes/Contactos"
METADATA_UNIT_LABEL = "Unidad de Negocio"

DEFAULT_DB_NAME = "nexora_multirrubro.sqlite"

# Afinidad Telegram (v5.4): fase 2 desde la 2.ª interacción; fase 3 a partir de este umbral
DEFAULT_AFINIDAD_FASE3_MIN = 10

# Embudo de consultoría — estado del prospecto (codificación interna 1–4)
FASES_CONSULTORIA: dict[int, str] = {
    1: "1-Contacto",
    2: "2-Saneamiento de dudas",
    3: "3-Listo para cierre humano",
    4: "4-Acuerdo firmado",
}


def db_path() -> Path:
    p = Path(LOCAL_DB_FILE)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS unidades_negocio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            sector TEXT,
            notas TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS clientes_contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            unidad_negocio_id INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (unidad_negocio_id) REFERENCES unidades_negocio(id)
        );
        CREATE INDEX IF NOT EXISTS idx_cc_unidad ON clientes_contactos(unidad_negocio_id);
        CREATE TABLE IF NOT EXISTS gestion_consultoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_prospecto TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            estado_prospecto INTEGER NOT NULL CHECK (estado_prospecto >= 1 AND estado_prospecto <= 4),
            interes TEXT,
            notas TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_gc_fase ON gestion_consultoria(estado_prospecto);
        CREATE TABLE IF NOT EXISTS telegram_afinidad (
            user_id TEXT PRIMARY KEY,
            display_name TEXT,
            username TEXT,
            interaction_count INTEGER NOT NULL DEFAULT 0,
            trust_level INTEGER NOT NULL DEFAULT 1 CHECK (trust_level >= 1 AND trust_level <= 3),
            last_topic_snippet TEXT,
            first_seen_at TEXT DEFAULT (datetime('now')),
            last_interaction_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_ta_trust ON telegram_afinidad(trust_level);
        CREATE TABLE IF NOT EXISTS ia_contabilidad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            monto REAL NOT NULL,
            fecha TEXT,
            proveedor TEXT,
            cuit_id TEXT,
            concepto TEXT,
            tipo TEXT CHECK (tipo IN ('ingreso', 'egreso')),
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_cont_fecha ON ia_contabilidad(fecha);
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            channel TEXT NOT NULL, -- 'telegram' o 'whatsapp'
            role TEXT NOT NULL,    -- 'user' o 'assistant' o 'system'
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_chat_user ON conversation_history(user_id);
        """
    )
    conn.commit()


def get_connection() -> sqlite3.Connection:
    p = db_path()
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn


def _fase3_min() -> int:
    try:
        v = int(os.environ.get("TELEGRAM_AFINIDAD_FASE3_MIN", DEFAULT_AFINIDAD_FASE3_MIN))
        return max(2, v)
    except ValueError:
        return DEFAULT_AFINIDAD_FASE3_MIN


def _compute_phase_and_trust(interaction_count: int, fase3_min: int) -> tuple[int, int]:
    """Fase 1: primer contacto; 2: recurrente; 3: confianza consolidada. trust_level 1–3 alineado."""
    if interaction_count <= 1:
        return 1, 1
    if interaction_count < fase3_min:
        return 2, 2
    return 3, 3


def record_telegram_interaction(
    user_id: str,
    display_name: str | None = None,
    username: str | None = None,
    topic_snippet: str | None = None,
) -> dict[str, Any]:
    """
    Registra interacción por user_id en nexora_multirrubro.sqlite: contador y nivel de confianza (1–3).
    Devuelve phase, trust_level y el tema previo (para continuidad conversacional).
    """
    fase3_min = _fase3_min()
    snippet = (topic_snippet or "").strip()
    if len(snippet) > 400:
        snippet = snippet[:397] + "..."

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM telegram_afinidad WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        prev_topic = (row["last_topic_snippet"] if row else None) or ""
        new_count = (int(row["interaction_count"]) if row else 0) + 1
        phase, trust = _compute_phase_and_trust(new_count, fase3_min)

        if row:
            final_name = display_name if display_name is not None else row["display_name"]
            final_uname = username if username is not None else row["username"]
            conn.execute(
                """
                UPDATE telegram_afinidad SET
                    display_name = ?, username = ?, interaction_count = ?, trust_level = ?,
                    last_topic_snippet = ?, last_interaction_at = datetime('now')
                WHERE user_id = ?
                """,
                (final_name, final_uname, new_count, trust, snippet, user_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO telegram_afinidad
                (user_id, display_name, username, interaction_count, trust_level, last_topic_snippet, last_interaction_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (user_id, display_name, username, new_count, trust, snippet),
            )
        conn.commit()

    return {
        "user_id": user_id,
        "interaction_count": new_count,
        "trust_level": trust,
        "phase": phase,
        "previous_topic_snippet": prev_topic,
        "fase3_min": fase3_min,
    }


def operational_metrics() -> dict[str, Any]:
    """Métricas agregadas interpretables para distintos flujos de ingresos (por unidad / sector)."""
    with get_connection() as conn:
        unidades = conn.execute("SELECT COUNT(*) FROM unidades_negocio").fetchone()[0]
        contactos = conn.execute("SELECT COUNT(*) FROM clientes_contactos").fetchone()[0]
        rows = conn.execute(
            """
            SELECT u.id, u.nombre, u.sector, COUNT(c.id) AS num_contactos
            FROM unidades_negocio u
            LEFT JOIN clientes_contactos c ON c.unidad_negocio_id = u.id
            GROUP BY u.id
            ORDER BY u.nombre
            """
        ).fetchall()
    por_unidad = [
        {
            METADATA_UNIT_LABEL: r["nombre"],
            "sector": r["sector"] or "—",
            METADATA_ENTITY_LABEL: r["num_contactos"],
        }
        for r in rows
    ]
    return {
        "db_path": str(db_path()),
        "total_unidades_negocio": unidades,
        "total_clientes_contactos": contactos,
        "desglose_por_unidad": por_unidad,
    }


def embudo_consultoria_metrics() -> dict[str, Any]:
    """Conteos por fase del embudo (consultoría / leads)."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT estado_prospecto, COUNT(*) AS n
            FROM gestion_consultoria
            GROUP BY estado_prospecto
            """
        ).fetchall()
    counts = {k: 0 for k in FASES_CONSULTORIA}
    for r in rows:
        estado = int(r["estado_prospecto"])
        if estado in counts:
            counts[estado] = int(r["n"])
    por_fase = [
        {
            "fase": FASES_CONSULTORIA[k],
            "codigo_fase": k,
            "prospectos": counts[k],
        }
        for k in sorted(FASES_CONSULTORIA.keys())
    ]
    total = sum(counts.values())
    return {"por_fase": por_fase, "total_prospectos": total, "conteos": counts}


def flash_resumen_pendientes_texto(max_chars: int = 900) -> str:
    """
    Resumen breve (~15 s al hablar) de unidades de negocio y embudo de consultoría pendiente.
    Usado por Sentinel / visión v5.6 tras identificar al Creador.
    """
    lines: list[str] = []
    try:
        with get_connection() as conn:
            urows = conn.execute(
                """
                SELECT nombre, COALESCE(sector, '') AS sector, COALESCE(notas, '') AS notas
                FROM unidades_negocio ORDER BY id DESC LIMIT 12
                """
            ).fetchall()
            crows = conn.execute(
                """
                SELECT nombre_prospecto, estado_prospecto, COALESCE(interes, '') AS interes
                FROM gestion_consultoria
                WHERE estado_prospecto < 4
                ORDER BY updated_at DESC LIMIT 15
                """
            ).fetchall()
    except Exception:
        return "No pude leer el resumen operativo en este momento."

    if urows:
        lines.append("Unidades de negocio:")
        for r in urows:
            sec = f", sector {r['sector']}" if r["sector"] else ""
            lines.append(f"  • {r['nombre']}{sec}.")
    if crows:
        lines.append("Consultoría — pendientes de cierre:")
        for r in crows:
            fase = FASES_CONSULTORIA.get(int(r["estado_prospecto"]), "?")
            inter = f" Interés: {r['interes']}." if r["interes"] else ""
            lines.append(f"  • {r['nombre_prospecto']} ({fase}).{inter}")
    if not lines:
        lines.append("Sin registros pendientes en unidades ni embudo; tablas vacías o al día.")

    text = " ".join(lines).replace("\n", " ")
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def registrar_prospecto_consultoria(
    nombre_prospecto: str,
    estado_prospecto: int,
    email: str | None = None,
    telefono: str | None = None,
    interes: str | None = None,
    notas: str | None = None,
) -> int:
    """Inserta o actualiza lógica mínima de lead; devuelve last row id."""
    if estado_prospecto not in FASES_CONSULTORIA:
        raise ValueError("estado_prospecto debe estar entre 1 y 4")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO gestion_consultoria
            (nombre_prospecto, email, telefono, estado_prospecto, interes, notas, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (nombre_prospecto, email, telefono, estado_prospecto, interes, notas),
        )
        conn.commit()
        return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def registrar_operacion_contable(
    user_id: str,
    monto: float,
    fecha: str | None = None,
    proveedor: str | None = None,
    cuit_id: str | None = None,
    concepto: str | None = None,
    tipo: str = "egreso",
) -> int:
    """Registra un movimiento contable extraído por la IA."""
    with get_connection() as conn:
        res = conn.execute(
            """
            INSERT INTO ia_contabilidad
            (user_id, monto, fecha, proveedor, cuit_id, concepto, tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, monto, fecha, proveedor, cuit_id, concepto, tipo),
        )
        conn.commit()
        return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def get_accounting_summary() -> dict[str, Any]:
    """Resumen rápido de ingresos y egresos."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT tipo, SUM(monto) as total
            FROM ia_contabilidad
            GROUP BY tipo
            """
        ).fetchall()
        summary = {row["tipo"]: row["total"] for row in rows}
        return {
            "ingresos": summary.get("ingreso", 0.0),
            "egresos": summary.get("egreso", 0.0),
            "balance": summary.get("ingreso", 0.0) - summary.get("egreso", 0.0),
        }


def save_message(user_id: str, channel: str, role: str, content: str) -> None:
    """Guarda un mensaje en el historial multinodal v8.2."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversation_history (user_id, channel, role, content) VALUES (?, ?, ?, ?)",
            (user_id, channel, role, content),
        )
        conn.commit()

def get_conversation_history(user_id: str, limit: int = 10) -> list[dict[str, str]]:
    """Recupera los últimos N mensajes de un hilo de conversación único."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM conversation_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        # Invertir para que estén en orden cronológico (viejo a nuevo)
        history = [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
        return history

def get_prospects_summary() -> list[dict[str, Any]]:
    """Resumen de prospectos para el Dashboard v8.2."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT nombre_prospecto, estado_prospecto, interes, created_at 
            FROM gestion_consultoria 
            ORDER BY created_at DESC LIMIT 10
            """
        ).fetchall()
        return [dict(r) for r in rows]
