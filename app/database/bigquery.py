import logging
from typing import Any, Mapping, Sequence

from google.cloud import bigquery

from app.database.connection import gcp_client_factory

logger = logging.getLogger("app.database.bigquery")


import json
import sqlite3
import time
from typing import Any, Mapping, Sequence

from google.cloud import bigquery

from app.database.connection import gcp_client_factory

logger = logging.getLogger("app.database.bigquery")


class MockRow:
    """Mock Row behaving like a BigQuery Row object."""
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self) -> Any:
        return self._data.keys()

    def values(self) -> Any:
        return self._data.values()

    def items(self) -> Any:
        return self._data.items()


class BigQueryManager:
    """Wrapper class managing interaction with BigQuery datasets and tables with SQLite local dev fallback."""

    def __init__(self, client: bigquery.Client = None) -> None:
        # Allow passing custom mock/test client, fall back to default factory
        self.use_fallback = False
        self.client = None
        self.conn = None

        # Always configure local SQLite database for local credentials/metadata
        self.conn = sqlite3.connect("local_metadata.db", check_same_thread=False)
        self._setup_local_tables()

        if client is not None:
            self.client = client
        else:
            try:
                self.client = gcp_client_factory.get_bigquery_client()
            except Exception as e:
                logger.warning(
                    f"BigQuery connection offline/unconfigured ({str(e)}). Falling back to local SQLite manager for queries."
                )
                self.use_fallback = True


    def _setup_local_tables(self) -> None:
        """Sets up required SQLite tables for metadata persistence when running locally."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    name TEXT,
                    roles TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    expression TEXT,
                    action TEXT,
                    priority INTEGER,
                    is_active INTEGER,
                    created_by TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulation_scenarios (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    parameters TEXT,
                    results TEXT,
                    base_dataset_id TEXT,
                    status TEXT,
                    results_url TEXT,
                    created_by TEXT,
                    created_at TEXT
                )
            """)
            try:
                cursor.execute("ALTER TABLE simulation_scenarios ADD COLUMN results TEXT")
            except Exception:
                pass
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_reports (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    query_executed TEXT,
                    export_format TEXT,
                    gcs_uri TEXT,
                    created_by TEXT,
                    created_at TEXT
                )
            """)
            # Note: file_uploads holds FileMetadata entities which have id as primary key
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_uploads (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    content_type TEXT,
                    size_bytes INTEGER,
                    gcs_uri TEXT,
                    public_url TEXT,
                    uploaded_by TEXT,
                    uploaded_at TEXT,
                    processed INTEGER
                )
            """)
            
            # Seed default hackathon demo user if not exists
            cursor.execute("SELECT id FROM users WHERE email = 'streamlineuser@streamline.com'")
            if not cursor.fetchone():
                from passlib.hash import bcrypt
                import uuid
                from datetime import datetime, timezone
                
                hashed_pw = bcrypt.hash("streamline")
                uid = "hackathon-seed-user-123"
                created_at = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    "INSERT INTO users (id, email, password_hash, name, roles, is_active, created_at) VALUES (?, 'streamlineuser@streamline.com', ?, 'StreamLine User', 'admin', 1, ?)",
                    (uid, hashed_pw, created_at)
                )
                logger.info("Hackathon seed user inserted successfully.")
                
            self.conn.commit()
            logger.info("Local SQLite metadata tables verified/created successfully.")
        except Exception as e:
            logger.critical(f"Failed to setup local SQLite database tables: {str(e)}")

    def execute_query(
        self, query: str, job_config: bigquery.QueryJobConfig = None
    ) -> Any:
        """Executes a SQL query against BigQuery (or local SQLite if in fallback mode).

        Returns a RowIterator (or list of MockRows) to process results.
        """
        if self.use_fallback:
            logger.debug(f"Executing query locally via SQLite: {query}")
            try:
                # Clean up BigQuery backticks and project/dataset prefixes
                clean_query = query.replace("`", "")
                clean_query = clean_query.replace("streamline_metadata.", "")
                clean_query = clean_query.replace("streamline_dataset.", "")
                # Map SQL boolean values to standard integer states
                clean_query = clean_query.replace("= TRUE", "= 1").replace("= FALSE", "= 0")
                clean_query = clean_query.replace("= true", "= 1").replace("= false", "= 0")

                cursor = self.conn.cursor()
                cursor.execute(clean_query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    row_dict = {}
                    for idx, col_name in enumerate(columns):
                        val = row[idx]
                        # De-serialize JSON fields
                        if col_name in {"parameters", "roles", "evidence", "results"}:
                            try:
                                if val:
                                    val = json.loads(val)
                            except Exception:
                                pass
                        row_dict[col_name] = val
                    results.append(MockRow(row_dict))
                return results
            except Exception as e:
                logger.error(f"Local SQLite query execution failed: {str(e)}")
                raise e

        logger.debug(f"Running BigQuery query: {query}")
        try:
            query_job = self.client.query(query, job_config=job_config)
            # Wait for query to finish
            results = query_job.result()
            return results
        except Exception as e:
            logger.error(f"BigQuery query execution failed: {str(e)}")
            raise e

    def insert_rows_json(
        self, dataset_id: str, table_id: str, json_rows: Sequence[Mapping[str, Any]]
    ) -> Sequence[dict[str, Any]]:
        """Performs a streaming insert of JSON rows into a BigQuery table (or SQLite if fallback).

        Returns a list of errors if any occurred, empty list otherwise.
        """
        if self.use_fallback:
            logger.debug(f"Local SQLite insertion of {len(json_rows)} rows into table '{table_id}'")
            try:
                cursor = self.conn.cursor()
                for row in json_rows:
                    row_data = {}
                    for k, v in row.items():
                        if isinstance(v, (dict, list)):
                            row_data[k] = json.dumps(v)
                        else:
                            row_data[k] = v

                    columns = list(row_data.keys())
                    placeholders = ", ".join(["?"] * len(columns))
                    # Allow insertion upserts
                    query = f"INSERT OR REPLACE INTO {table_id} ({', '.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(query, list(row_data.values()))
                self.conn.commit()
                return []
            except Exception as e:
                logger.error(f"Local SQLite insert failed: {str(e)}")
                return [{"error": str(e)}]

        logger.debug(f"Streaming {len(json_rows)} rows into {dataset_id}.{table_id}")
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            errors = self.client.insert_rows_json(table_ref, json_rows)
            if errors:
                logger.error(f"BigQuery streaming insert returned errors: {errors}")
            return errors
        except Exception as e:
            logger.error(f"BigQuery streaming insert failed: {str(e)}")
            raise e

