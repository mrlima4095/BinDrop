import os
import sqlite3

def PlainPostDB():
    conn = sqlite3.connect('mailserver.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            original_name TEXT NOT NULL,
            saved_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            upload_time TEXT NOT NULL,
            expire_time TEXT
        )
    """)
    
    conn.commit()
    conn.close()

PlainPostDB()