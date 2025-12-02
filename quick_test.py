#!/usr/bin/env python3
"""Quick test to verify PostgreSQL connection"""

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="personify",
        user="postgres",
        password="postgres"
    )
    print("✓ Successfully connected to PostgreSQL!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✓ PostgreSQL version: {version[0][:50]}...")
    
    cursor.execute("SELECT current_database();")
    db = cursor.fetchone()
    print(f"✓ Connected to database: {db[0]}")
    
    cursor.close()
    conn.close()
    print("\n✓✓✓ PostgreSQL is working perfectly!")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nTry running: docker-compose up -d postgres")

