from typing import List, Dict

SAMPLE_TEST_CASES: List[Dict[str, str]] = [
    {
        "id": "py-sql-injection",
        "title": "SQL Injection & Hardcoded Credential",
        "language": "python",
        "description": "Simulates an insecure web endpoint with dynamic SQL query concatenation, hardcoded API secret, and bare exception handling.",
        "code": """import os
import sqlite3

API_KEY = "sk-live-99218204918239012384"

def get_user_records(user_input):
    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()
    
    # Vulnerable dynamic SQL query string interpolation
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    print("Executing query:", query)
    
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except:
        # Bare except hides critical system errors
        pass
"""
    },
    {
        "id": "py-perf-leak",
        "title": "Nested O(n²) Loop & Unmanaged Resource",
        "language": "python",
        "description": "Illustrates algorithmic bottlenecks with quadratic lookup, unmanaged file handle leaks, and blocking sleep in request cycle.",
        "code": """import time

def match_user_transactions(users, transactions):
    matched = []
    
    # Quadratic nested loop: O(U * T) lookup complexity
    for user in users:
        for txn in transactions:
            if user['id'] == txn['user_id']:
                matched.append({'user': user['name'], 'amount': txn['amount']})
    
    # Resource leak: file opened without context manager
    log_file = open("audit.log", "a")
    log_file.write(f"Matched {len(matched)} records\\n")
    
    # Blocking synchronous sleep in worker thread
    time.sleep(2)
    return matched
"""
    },
    {
        "id": "js-insecure-eval",
        "title": "JavaScript Insecure Eval & Prototype Risk",
        "language": "javascript",
        "description": "Unsanitized user payload evaluated dynamically with eval(), creating severe Remote Code Execution (RCE) vulnerability.",
        "code": """const express = require('express');
const app = express();
app.use(express.json());

const JWT_SECRET = "super_secret_jwt_signing_key_12345";

app.post('/api/calculate', (req, res) => {
    const { formula, context } = req.body;
    
    // Critical Vulnerability: Direct eval of untrusted client formula
    try {
        const result = eval(formula);
        res.json({ success: true, result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
"""
    },
    {
        "id": "py-clean-refactor",
        "title": "Clean Python Function (Baseline Test)",
        "language": "python",
        "description": "A well-structured Python utility with type hints, context manager, and parameterized queries to test false positive resistance.",
        "code": """import os
import sqlite3
from typing import List, Optional, Tuple

DATABASE_URL = os.getenv("DB_PATH", "app.db")

def fetch_active_orders(user_id: int) -> List[Tuple[int, str, float]]:
    \"\"\"Safely retrieves active orders for a verified user.\"\"\"
    query = \"\"\"
        SELECT order_id, item_name, total_price 
        FROM customer_orders 
        WHERE user_id = ? AND status = 'ACTIVE'
    \"\"\"
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
"""
    }
]
