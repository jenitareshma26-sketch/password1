"""
Utility functions for the Password Generator application.
"""

import os
from datetime import datetime
from typing import Optional, List


class ClipboardManager:
    """Cross-platform clipboard manager with fallback."""

    def __init__(self):
        self._fallback_buffer = ""

    def copy(self, text: str) -> bool:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception:
            # Store in fallback buffer
            self._fallback_buffer = text
            return False

    def paste(self) -> Optional[str]:
        """Get text from clipboard."""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            return self._fallback_buffer if self._fallback_buffer else None

    def clear(self) -> bool:
        """Clear the clipboard."""
        try:
            import pyperclip
            pyperclip.copy('')
            return True
        except Exception:
            self._fallback_buffer = ""
            return True


# Global clipboard instance
_clipboard = ClipboardManager()


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard."""
    return _clipboard.copy(text)


def get_from_clipboard() -> Optional[str]:
    """Get text from system clipboard."""
    return _clipboard.paste()


def clear_clipboard() -> bool:
    """Clear the system clipboard."""
    return _clipboard.clear()


def format_datetime(dt_string: str) -> str:
    """Format datetime string for display."""
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%b %d, %Y %I:%M %p')
    except ValueError:
        return dt_string


def format_short_datetime(dt_string: str) -> str:
    """Format datetime string for short display."""
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%m/%d %I:%M %p')
    except ValueError:
        return dt_string


def ensure_directory(path: str) -> bool:
    """Ensure a directory exists, create if necessary."""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception:
        return False


def get_export_path(filename: str, export_dir: str = 'exports') -> str:
    """Get full path for export file."""
    ensure_directory(export_dir)
    return os.path.join(export_dir, filename)


def generate_filename(base_name: str, extension: str) -> str:
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}.{extension}"


def truncate_password(password: str, max_length: int = 30) -> str:
    """Truncate password for display with ellipsis."""
    if len(password) <= max_length:
        return password
    return password[:max_length - 3] + '...'


def mask_password(password: str, show_chars: int = 4) -> str:
    """Mask password for security display."""
    if len(password) <= show_chars * 2:
        return '*' * len(password)
    return password[:show_chars] + '*' * (len(password) - show_chars * 2) + password[-show_chars:]


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage with safety check."""
    if total == 0:
        return 0
    return round((value / total) * 100, 2)


# Security tips database
SECURITY_TIPS = [
    {
        'title': 'Use Unique Passwords Everywhere',
        'content': 'Never reuse passwords across different accounts. Each account should have its own unique, strong password.',
        'category': 'Best Practice'
    },
    {
        'title': 'Length Over Complexity',
        'content': 'A longer password is generally more secure than a shorter complex one. Aim for at least 12 characters.',
        'category': 'Password Strength'
    },
    {
        'title': 'Use a Password Manager',
        'content': 'Password managers securely store all your passwords, so you only need to remember one master password.',
        'category': 'Tools'
    },
    {
        'title': 'Enable Two-Factor Authentication',
        'content': '2FA adds an extra layer of security. Even if your password is compromised, attackers need the second factor.',
        'category': 'Best Practice'
    },
    {
        'title': 'Avoid Personal Information',
        'content': 'Never use personal details like birthdays, names, or addresses in passwords - these are easily guessed.',
        'category': 'What to Avoid'
    },
    {
        'title': 'Check for Breaches',
        'content': 'Regularly check if your accounts have been compromised using breach monitoring services.',
        'category': 'Monitoring'
    },
    {
        'title': 'Change Compromised Passwords Immediately',
        'content': 'If you learn a service was breached or suspicious activity detected, change your password immediately.',
        'category': 'Incident Response'
    },
    {
        'title': 'Avoid Dictionary Words',
        'content': 'Dictionary words are vulnerable to dictionary attacks. Use random character combinations instead.',
        'category': 'What to Avoid'
    },
    {
        'title': 'Secure Your Master Password',
        'content': 'Your password manager master password should be the strongest - memorize it, never write it down.',
        'category': 'Critical'
    },
    {
        'title': 'Review App Permissions',
        'content': 'Regularly review which apps have access to your accounts and revoke access you no longer need.',
        'category': 'Maintenance'
    },
    {
        'title': 'Use Different Passwords for Banking',
        'content': 'Financial accounts should have unique, complex passwords not used anywhere else.',
        'category': 'Best Practice'
    },
    {
        'title': 'Be Wary of Phishing',
        'content': 'Never enter passwords on suspicious links. Always verify the URL and use bookmarks for important sites.',
        'category': 'Threats'
    }
]


def get_security_tip(index: int = None) -> dict:
    """Get a security tip by index or random."""
    import random
    if index is not None and 0 <= index < len(SECURITY_TIPS):
        return SECURITY_TIPS[index]
    return random.choice(SECURITY_TIPS)


def get_all_security_tips() -> List[dict]:
    """Get all security tips."""
    return SECURITY_TIPS


def get_tips_by_category(category: str) -> List[dict]:
    """Get security tips filtered by category."""
    return [tip for tip in SECURITY_TIPS if tip['category'] == category]


# Color constants for strength indication
STRENGTH_COLORS = {
    'Very Weak': '#FF4444',
    'Weak': '#FF8844',
    'Fair': '#FFAA44',
    'Strong': '#88CC44',
    'Very Strong': '#44DD44'
}


def get_strength_color(strength: str, dark_mode: bool = True) -> str:
    """Get color for strength level."""
    return STRENGTH_COLORS.get(strength, '#888888')


# Keyboard shortcuts info
KEYBOARD_SHORTCUTS = [
    ('Ctrl+G', 'Generate new password'),
    ('Ctrl+C', 'Copy current password'),
    ('Ctrl+Shift+C', 'Clear clipboard'),
    ('Ctrl+S', 'Open settings'),
    ('Ctrl+H', 'View password history'),
    ('Ctrl+E', 'Export passwords'),
    ('Ctrl+R', 'Regenerate password'),
    ('Ctrl+T', 'Toggle theme'),
    ('F1', 'Show help'),
    ('Escape', 'Close dialogs')
]


def get_keyboard_shortcuts() -> List[tuple]:
    """Get list of keyboard shortcuts."""
    return KEYBOARD_SHORTCUTS
