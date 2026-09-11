"""
Database Layer for FlowMind
Supports Supabase PostgreSQL with transparent local SQLite fallback.
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

DB_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(DB_DIR, "flowmind.db")


class SQLiteQueryBuilder:
    """
    Fluent Query Builder matching Supabase Python SDK interface (.table().select().eq().execute())
    """
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name
        self.select_columns = "*"
        self.filters = []
        self.order_by = None
        self.order_desc = False
        self.limit_val = None
        self._action = "SELECT"
        self._insert_data = None
        self._update_data = None

    def select(self, columns: str = "*"):
        self._action = "SELECT"
        self.select_columns = columns
        return self

    def insert(self, data: Any):
        self._action = "INSERT"
        self._insert_data = data if isinstance(data, list) else [data]
        return self

    def update(self, data: Dict[str, Any]):
        self._action = "UPDATE"
        self._update_data = data
        return self

    def delete(self):
        self._action = "DELETE"
        return self

    def eq(self, column: str, value: Any):
        self.filters.append((column, "=", value))
        return self

    def neq(self, column: str, value: Any):
        self.filters.append((column, "!=", value))
        return self

    def order(self, column: str, desc: bool = False):
        self.order_by = column
        self.order_desc = desc
        return self

    def limit(self, count: int):
        self.limit_val = count
        return self

    def execute(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            if self._action == "SELECT":
                query = f"SELECT {self.select_columns} FROM {self.table_name}"
                params = []
                if self.filters:
                    where_clauses = [f"{col} {op} ?" for col, op, _ in self.filters]
                    query += " WHERE " + " AND ".join(where_clauses)
                    params.extend([val for _, _, val in self.filters])

                if self.order_by:
                    query += f" ORDER BY {self.order_by} {'DESC' if self.order_desc else 'ASC'}"
                if self.limit_val:
                    query += f" LIMIT {self.limit_val}"

                cursor.execute(query, params)
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                return QueryResponse(data=data, count=len(data))

            elif self._action == "INSERT":
                inserted_rows = []
                for item in self._insert_data:
                    cols = list(item.keys())
                    placeholders = ["?"] * len(cols)
                    values = [
                        json.dumps(item[c]) if isinstance(item[c], (dict, list)) else item[c]
                        for c in cols
                    ]
                    query = f"INSERT OR REPLACE INTO {self.table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                    cursor.execute(query, values)
                    inserted_rows.append(item)
                conn.commit()
                return QueryResponse(data=inserted_rows, count=len(inserted_rows))

            elif self._action == "UPDATE":
                set_clauses = [f"{col} = ?" for col in self._update_data.keys()]
                params = [
                    json.dumps(v) if isinstance(v, (dict, list)) else v
                    for v in self._update_data.values()
                ]
                query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}"
                if self.filters:
                    where_clauses = [f"{col} {op} ?" for col, op, _ in self.filters]
                    query += " WHERE " + " AND ".join(where_clauses)
                    params.extend([val for _, _, val in self.filters])

                cursor.execute(query, params)
                conn.commit()
                return QueryResponse(data=[self._update_data], count=cursor.rowcount)

            elif self._action == "DELETE":
                query = f"DELETE FROM {self.table_name}"
                params = []
                if self.filters:
                    where_clauses = [f"{col} {op} ?" for col, op, _ in self.filters]
                    query += " WHERE " + " AND ".join(where_clauses)
                    params.extend([val for _, _, val in self.filters])
                cursor.execute(query, params)
                conn.commit()
                return QueryResponse(data=[], count=cursor.rowcount)

        finally:
            conn.close()


class QueryResponse:
    def __init__(self, data: List[Dict[str, Any]], count: int = 0):
        self.data = data
        self.count = count


class SQLiteClient:
    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                applicant_name TEXT NOT NULL,
                applicant_age INTEGER NOT NULL,
                business_name TEXT NOT NULL,
                business_registration_number TEXT,
                operating_months INTEGER NOT NULL,
                loan_amount REAL NOT NULL,
                monthly_turnover REAL NOT NULL,
                purpose TEXT NOT NULL,
                purpose_category TEXT NOT NULL,
                bank_statement_account_name TEXT,
                status TEXT NOT NULL,
                ai_recommendation TEXT,
                briefing_text TEXT,
                generated_letter TEXT,
                letter_validation_status TEXT,
                human_decision TEXT,
                officer_id TEXT,
                human_notes TEXT,
                is_override INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Audit decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                officer_id TEXT NOT NULL,
                notes TEXT,
                is_override INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        """)
        conn.commit()
        conn.close()

    def table(self, table_name: str) -> SQLiteQueryBuilder:
        return SQLiteQueryBuilder(self.db_path, table_name)


# Initialize client: use Supabase if keys provided, else local SQLite
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"):
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = SQLiteClient()
else:
    supabase = SQLiteClient()


# ---------------- Helper Functions for Workflow & Dashboard ----------------

def load_briefing(application_id: str) -> str:
    """Loads the briefing text stored for an escalated application."""
    res = supabase.table("applications").select("briefing_text, business_name").eq("id", application_id).execute()
    if res.data and len(res.data) > 0:
        return res.data[0].get("briefing_text") or "No briefing text recorded."
    return "Application not found."

def save_human_decision(
    application_id: str,
    decision: str,
    officer_id: str = "officer_1",
    notes: str = "",
) -> Dict[str, Any]:
    """
    Saves a loan officer's review decision and marks override flag if decision differs from AI.
    """
    app_res = supabase.table("applications").select("*").eq("id", application_id).execute()
    if not app_res.data:
        raise ValueError(f"Application {application_id} not found.")

    record = app_res.data[0]
    ai_rec = record.get("ai_recommendation") or ""

    # Determine if human decision is an override
    is_override = False
    if "approve" in ai_rec.lower() and decision in ["human_declined", "human_info_requested"]:
        is_override = True
    elif "decline" in ai_rec.lower() and decision in ["human_approved", "human_info_requested"]:
        is_override = True

    timestamp = datetime.now().isoformat()

    # Update application record
    supabase.table("applications").update({
        "human_decision": decision,
        "officer_id": officer_id,
        "human_notes": notes,
        "is_override": 1 if is_override else 0,
        "status": decision,
        "updated_at": timestamp,
    }).eq("id", application_id).execute()

    # Insert into decisions audit
    audit_entry = {
        "application_id": application_id,
        "decision": decision,
        "officer_id": officer_id,
        "notes": notes,
        "is_override": 1 if is_override else 0,
        "created_at": timestamp,
    }
    supabase.table("decisions_audit").insert(audit_entry).execute()

    return {"status": "success", "is_override": is_override, "decision": decision}

def update_status(application_id: str, new_status: str) -> Dict[str, Any]:
    """Updates the status of an application."""
    timestamp = datetime.now().isoformat()
    supabase.table("applications").update({
        "status": new_status,
        "updated_at": timestamp,
    }).eq("id", application_id).execute()
    return {"status": "updated", "new_status": new_status}

def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Computes real-time metrics from the database:
    - Total applications
    - % handled autonomously
    - % escalated
    - Human override rate (% of auto / AI-guided decisions corrected by human)
    """
    res = supabase.table("applications").select("*").execute()
    rows = res.data or []
    total = len(rows)

    if total == 0:
        return {
            "total_applications": 0,
            "auto_approved": 0,
            "auto_declined": 0,
            "escalated_pending": 0,
            "human_reviewed": 0,
            "autonomous_pct": 0.0,
            "escalated_pct": 0.0,
            "human_override_pct": 0.0,
            "override_count": 0,
            "total_human_decisions": 0,
        }

    auto_approved = sum(1 for r in rows if r.get("status") == "auto_approved")
    auto_declined = sum(1 for r in rows if r.get("status") == "auto_declined")
    escalated_pending = sum(1 for r in rows if r.get("status") == "escalated")
    human_decided = sum(1 for r in rows if r.get("status") in ["human_approved", "human_declined", "human_info_requested"])

    total_autonomous = auto_approved + auto_declined
    total_escalated_overall = escalated_pending + human_decided

    autonomous_pct = (total_autonomous / total) * 100
    escalated_pct = (total_escalated_overall / total) * 100

    overrides = sum(1 for r in rows if r.get("is_override") in [1, True])
    override_pct = (overrides / human_decided * 100) if human_decided > 0 else 0.0

    return {
        "total_applications": total,
        "auto_approved": auto_approved,
        "auto_declined": auto_declined,
        "escalated_pending": escalated_pending,
        "human_reviewed": human_decided,
        "autonomous_count": total_autonomous,
        "escalated_total": total_escalated_overall,
        "autonomous_pct": round(autonomous_pct, 1),
        "escalated_pct": round(escalated_pct, 1),
        "human_override_pct": round(override_pct, 1),
        "override_count": overrides,
        "total_human_decisions": human_decided,
    }
