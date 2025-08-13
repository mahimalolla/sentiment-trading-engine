import sqlite3, os, time
from typing import Iterable, Dict, Any
from .config import DB_PATH

DDL_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_ts INTEGER,
  params_json TEXT
);
"""
DDL_HEADLINES = """
CREATE TABLE IF NOT EXISTS headlines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER,
  ticker TEXT,
  title TEXT,
  url TEXT,
  source TEXT,
  published_at TEXT,
  pos_hits INTEGER,
  neg_hits INTEGER,
  FOREIGN KEY(run_id) REFERENCES runs(id)
);
"""

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = get_conn()
    cur = con.cursor()
    cur.execute(DDL_RUNS)
    cur.execute(DDL_HEADLINES)
    con.commit()
    con.close()

def insert_run(params_json: str) -> int:
    con = get_conn()
    cur = con.cursor()
    cur.execute("INSERT INTO runs(run_ts, params_json) VALUES (?,?)", (int(time.time()), params_json))
    run_id = cur.lastrowid
    con.commit(); con.close()
    return run_id

def insert_headlines(run_id: int, rows: Iterable[Dict[str,Any]]):
    con = get_conn()
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO headlines(run_id,ticker,title,url,source,published_at,pos_hits,neg_hits) VALUES (?,?,?,?,?,?,?,?)",
        [(run_id, r.get("ticker"), r.get("title"), r.get("url"), r.get("source"),
          r.get("published_at"), r.get("pos_hits",0), r.get("neg_hits",0)) for r in rows]
    )
    con.commit(); con.close()
