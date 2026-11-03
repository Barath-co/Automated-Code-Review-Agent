export const BENCHMARK_PRESETS = [
  {
    id: "py-sql-injection",
    title: "SQL injection in user login",
    language: "python",
    badge: "Critical",
    description: "Concatenated SQL queries vulnerable to SQL injection with exposed API key.",
    code: `import os
import sqlite3

API_KEY = "sk-live-99218204918239012384"

def get_user_records(user_input):
    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()
    
    # Critical Vulnerability: Dynamic SQL query string interpolation
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    print("Executing query:", query)
    
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except:
        # Bare except hides critical system errors
        pass
`
  },
  {
    id: "py-perf-leak",
    title: "O(n²) nested loop & memory leak",
    language: "python",
    badge: "High",
    description: "Quadratic iteration with unclosed file descriptor and blocking sleep.",
    code: `import time

def match_user_transactions(users, transactions):
    matched = []
    
    # Quadratic nested iteration: O(U * T) computational complexity
    for user in users:
        for txn in transactions:
            if user['id'] == txn['user_id']:
                matched.append({'user': user['name'], 'amount': txn['amount']})
    
    # Resource Leak: File opened without a context manager
    log_file = open("transaction_audit.log", "a")
    log_file.write(f"Matched {len(matched)} transactions\\n")
    
    # Blocking synchronous sleep in worker thread
    time.sleep(2)
    return matched
`
  },
  {
    id: "js-insecure-eval",
    title: "Remote code execution via eval()",
    language: "javascript",
    badge: "Critical",
    description: "Direct evaluation of untrusted client payload via eval().",
    code: `const express = require('express');
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
`
  },
  {
    id: "py-clean-refactor",
    title: "Clean database query function",
    language: "python",
    badge: "Safe",
    description: "Type-hinted, parameterized SQL query wrapped with context manager.",
    code: `import os
import sqlite3
from typing import List, Optional, Tuple

DATABASE_URL = os.getenv("DB_PATH", "app.db")

def fetch_active_orders(user_id: int) -> List[Tuple[int, str, float]]:
    """Safely retrieves active orders for a verified user using parameterized query."""
    query = """
        SELECT order_id, item_name, total_price 
        FROM customer_orders 
        WHERE user_id = ? AND status = 'ACTIVE'
    """
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
`
  }
];
