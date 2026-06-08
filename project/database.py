"""
Database module for Password Generator application.
Handles all SQLite operations for password history and settings.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'passwords.db')


class Database:
    """SQLite database manager for password generator."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_database_directory()
        self._initialize_database()

    def _ensure_database_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Password History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT NOT NULL,
                strength TEXT NOT NULL,
                length INTEGER NOT NULL,
                entropy REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_name TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        ''')

        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_generated INTEGER DEFAULT 0,
                date_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Initialize statistics if empty
        cursor.execute('SELECT COUNT(*) FROM statistics')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO statistics (total_generated) VALUES (0)')

        # Default settings
        default_settings = {
            'default_length': '16',
            'default_security_level': 'Strong',
            'auto_copy': 'true',
            'theme': 'dark',
            'export_directory': 'exports',
            'show_strength_colors': 'true',
            'exclude_similar': 'false',
            'exclude_ambiguous': 'false',
            'prevent_repeated': 'false',
            'prevent_sequential': 'false'
        }

        for name, value in default_settings.items():
            cursor.execute('''
                INSERT OR IGNORE INTO settings (setting_name, setting_value)
                VALUES (?, ?)
            ''', (name, value))

        conn.commit()
        conn.close()

    # ==================== Password History Operations ====================

    def add_password(self, password: str, strength: str, length: int, entropy: float = 0.0) -> int:
        """Add a generated password to history."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO password_history (password, strength, length, entropy, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (password, strength, length, entropy, datetime.now()))

        # Update statistics
        cursor.execute('UPDATE statistics SET total_generated = total_generated + 1')

        password_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return password_id

    def get_all_passwords(self) -> List[Dict]:
        """Get all password history entries."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, password, strength, length, entropy, created_at
            FROM password_history
            ORDER BY created_at DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_passwords(self, search_term: str) -> List[Dict]:
        """Search password history by strength or date."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, password, strength, length, entropy, created_at
            FROM password_history
            WHERE strength LIKE ? OR created_at LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_password(self, password_id: int) -> bool:
        """Delete a specific password entry."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM password_history WHERE id = ?', (password_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    def clear_history(self) -> int:
        """Clear all password history."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM password_history')
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()
        return deleted_count

    def get_history_count(self) -> int:
        """Get total count of passwords in history."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM password_history')
        count = cursor.fetchone()[0]

        conn.close()
        return count

    # ==================== Settings Operations ====================

    def get_setting(self, setting_name: str) -> Optional[str]:
        """Get a setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', (setting_name,))
        row = cursor.fetchone()

        conn.close()
        return row['setting_value'] if row else None

    def set_setting(self, setting_name: str, setting_value: str) -> bool:
        """Set a setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO settings (setting_name, setting_value)
            VALUES (?, ?)
        ''', (setting_name, setting_value))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings as a dictionary."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT setting_name, setting_value FROM settings')
        rows = cursor.fetchall()

        conn.close()
        return {row['setting_name']: row['setting_value'] for row in rows}

    # ==================== Statistics Operations ====================

    def get_statistics(self) -> Dict:
        """Get usage statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total generated
        cursor.execute('SELECT total_generated FROM statistics LIMIT 1')
        total_row = cursor.fetchone()
        total_generated = total_row['total_generated'] if total_row else 0

        # Strength distribution
        cursor.execute('''
            SELECT strength, COUNT(*) as count
            FROM password_history
            GROUP BY strength
        ''')
        strength_distribution = {row['strength']: row['count'] for row in cursor.fetchall()}

        # Average length
        cursor.execute('SELECT AVG(length) FROM password_history')
        avg_length_row = cursor.fetchone()
        avg_length = avg_length_row[0] if avg_length_row[0] else 0

        # Average entropy
        cursor.execute('SELECT AVG(entropy) FROM password_history')
        avg_entropy_row = cursor.fetchone()
        avg_entropy = avg_entropy_row[0] if avg_entropy_row[0] else 0

        # Recent generation trend (last 7 days)
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM password_history
            WHERE created_at >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''')
        trend_data = {row['date']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            'total_generated': total_generated,
            'strength_distribution': strength_distribution,
            'average_length': round(avg_length, 2),
            'average_entropy': round(avg_entropy, 2),
            'trend_data': trend_data
        }

    def reset_statistics(self) -> bool:
        """Reset all statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE statistics SET total_generated = 0')

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def export_history_to_list(self) -> List[List]:
        """Export history as a list for reports."""
        passwords = self.get_all_passwords()
        return [
            [p['password'], p['strength'], p['length'], p['created_at']]
            for p in passwords
        ]
