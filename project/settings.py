"""
Settings management module for Password Generator.
"""

from dataclasses import dataclass
from typing import Optional
from database import Database


@dataclass
class AppSettings:
    """Application settings dataclass."""
    default_length: int = 16
    default_security_level: str = 'Strong'
    auto_copy: bool = True
    theme: str = 'dark'
    export_directory: str = 'exports'
    show_strength_colors: bool = True
    exclude_similar: bool = False
    exclude_ambiguous: bool = False
    prevent_repeated: bool = False
    prevent_sequential: bool = False
    min_uppercase: int = 0
    min_lowercase: int = 0
    min_numbers: int = 0
    min_symbols: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'AppSettings':
        """Create settings from dictionary."""
        return cls(
            default_length=int(data.get('default_length', 16)),
            default_security_level=data.get('default_security_level', 'Strong'),
            auto_copy=data.get('auto_copy', 'true').lower() == 'true',
            theme=data.get('theme', 'dark'),
            export_directory=data.get('export_directory', 'exports'),
            show_strength_colors=data.get('show_strength_colors', 'true').lower() == 'true',
            exclude_similar=data.get('exclude_similar', 'false').lower() == 'true',
            exclude_ambiguous=data.get('exclude_ambiguous', 'false').lower() == 'true',
            prevent_repeated=data.get('prevent_repeated', 'false').lower() == 'true',
            prevent_sequential=data.get('prevent_sequential', 'false').lower() == 'true',
            min_uppercase=int(data.get('min_uppercase', 0)),
            min_lowercase=int(data.get('min_lowercase', 0)),
            min_numbers=int(data.get('min_numbers', 0)),
            min_symbols=int(data.get('min_symbols', 0))
        )

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            'default_length': str(self.default_length),
            'default_security_level': self.default_security_level,
            'auto_copy': 'true' if self.auto_copy else 'false',
            'theme': self.theme,
            'export_directory': self.export_directory,
            'show_strength_colors': 'true' if self.show_strength_colors else 'false',
            'exclude_similar': 'true' if self.exclude_similar else 'false',
            'exclude_ambiguous': 'true' if self.exclude_ambiguous else 'false',
            'prevent_repeated': 'true' if self.prevent_repeated else 'false',
            'prevent_sequential': 'true' if self.prevent_sequential else 'false',
            'min_uppercase': str(self.min_uppercase),
            'min_lowercase': str(self.min_lowercase),
            'min_numbers': str(self.min_numbers),
            'min_symbols': str(self.min_symbols)
        }


class SettingsManager:
    """Manager for application settings persistence."""

    # Valid theme options
    THEMES = ['dark', 'light']

    # Valid security levels
    SECURITY_LEVELS = ['Basic', 'Medium', 'Strong', 'Ultra Secure']

    # Export formats
    EXPORT_FORMATS = ['txt', 'csv', 'xlsx', 'pdf']

    def __init__(self, db: Database = None):
        self.db = db if db else Database()
        self._settings: Optional[AppSettings] = None

    def get_settings(self) -> AppSettings:
        """Load settings from database."""
        if self._settings is None:
            settings_dict = self.db.get_all_settings()
            self._settings = AppSettings.from_dict(settings_dict)
        return self._settings

    def save_settings(self, settings: AppSettings) -> bool:
        """Save settings to database."""
        settings_dict = settings.to_dict()
        success = True

        for name, value in settings_dict.items():
            if not self.db.set_setting(name, value):
                success = False

        self._settings = settings
        return success

    def update_setting(self, name: str, value) -> bool:
        """Update a single setting."""
        str_value = str(value) if not isinstance(value, str) else value
        success = self.db.set_setting(name, str_value)

        if success and self._settings:
            if name == 'default_length':
                self._settings.default_length = int(str_value)
            elif name == 'theme':
                self._settings.theme = str_value
            elif name == 'auto_copy':
                self._settings.auto_copy = str_value.lower() == 'true'
            elif name == 'exclude_similar':
                self._settings.exclude_similar = str_value.lower() == 'true'
            elif name == 'exclude_ambiguous':
                self._settings.exclude_ambiguous = str_value.lower() == 'true'
            elif name == 'prevent_repeated':
                self._settings.prevent_repeated = str_value.lower() == 'true'
            elif name == 'prevent_sequential':
                self._settings.prevent_sequential = str_value.lower() == 'true'

        return success

    def reset_to_defaults(self) -> AppSettings:
        """Reset settings to defaults."""
        default_settings = AppSettings()
        self.save_settings(default_settings)
        return default_settings

    def get_default_length_for_level(self, level: str) -> int:
        """Get default length for a security level."""
        lengths = {
            'Basic': 10,
            'Medium': 14,
            'Strong': 20,
            'Ultra Secure': 32
        }
        return lengths.get(level, 16)

    def validate_length(self, length: int, level: str = None) -> tuple:
        """Validate password length."""
        if length < 4:
            return False, 'Password must be at least 4 characters'
        if length > 128:
            return False, 'Password cannot exceed 128 characters'

        if level:
            min_len, max_len = self.get_level_length_range(level)
            if length < min_len:
                return False, f'Password should be at least {min_len} characters for {level} level'
            if length > max_len:
                return False, f'Password should not exceed {max_len} characters for {level} level'

        return True, 'Valid length'

    def get_level_length_range(self, level: str) -> tuple:
        """Get recommended length range for a security level."""
        ranges = {
            'Basic': (8, 10),
            'Medium': (12, 16),
            'Strong': (16, 24),
            'Ultra Secure': (24, 64)
        }
        return ranges.get(level, (8, 128))


class ThemeManager:
    """Manager for application theming."""

    # Dark theme colors (cybersecurity inspired)
    DARK_THEME = {
        'bg_primary': '#1a1a2e',
        'bg_secondary': '#16213e',
        'bg_tertiary': '#0f3460',
        'bg_card': '#1e1e3f',
        'bg_input': '#2d2d4f',
        'text_primary': '#E4E4E7',
        'text_secondary': '#A1A1AA',
        'text_muted': '#71717A',
        'accent_primary': '#6366f1',
        'accent_secondary': '#8b5cf6',
        'accent_gradient_start': '#6366f1',
        'accent_gradient_end': '#8b5cf6',
        'success': '#22c55e',
        'warning': '#eab308',
        'error': '#ef4444',
        'info': '#3b82f6',
        'border': '#374151',
        'border_light': '#4b5563'
    }

    # Light theme colors
    LIGHT_THEME = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F4F4F5',
        'bg_tertiary': '#E4E4E7',
        'bg_card': '#FFFFFF',
        'bg_input': '#FAFAFA',
        'text_primary': '#18181B',
        'text_secondary': '#3F3F46',
        'text_muted': '#71717A',
        'accent_primary': '#6366f1',
        'accent_secondary': '#8b5cf6',
        'accent_gradient_start': '#6366f1',
        'accent_gradient_end': '#8b5cf6',
        'success': '#16a34a',
        'warning': '#ca8a04',
        'error': '#dc2626',
        'info': '#2563eb',
        'border': '#D4D4D8',
        'border_light': '#E4E4E7'
    }

    def __init__(self, settings_manager: SettingsManager):
        self.settings_manager = settings_manager
        self._current_theme = None

    def get_theme(self) -> dict:
        """Get current theme colors."""
        if self._current_theme is None:
            settings = self.settings_manager.get_settings()
            if settings.theme == 'dark':
                self._current_theme = self.DARK_THEME
            else:
                self._current_theme = self.LIGHT_THEME
        return self._current_theme

    def toggle_theme(self) -> dict:
        """Toggle between dark and light theme."""
        settings = self.settings_manager.get_settings()
        new_theme = 'light' if settings.theme == 'dark' else 'dark'
        self.settings_manager.update_setting('theme', new_theme)

        if new_theme == 'dark':
            self._current_theme = self.DARK_THEME
        else:
            self._current_theme = self.LIGHT_THEME

        return self._current_theme

    def set_theme(self, theme_name: str) -> dict:
        """Set specific theme."""
        if theme_name == 'dark':
            self._current_theme = self.DARK_THEME
        else:
            self._current_theme = self.LIGHT_THEME

        self.settings_manager.update_setting('theme', theme_name)
        return self._current_theme
