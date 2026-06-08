"""
Password Generator module with cryptographically secure generation.
"""

import secrets
import string
import math
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PasswordAnalysis:
    """Analysis result for a password."""
    length: int
    entropy: float
    strength: str
    strength_score: int
    crack_time: str
    suggestions: List[str]
    has_uppercase: bool
    has_lowercase: bool
    has_numbers: bool
    has_symbols: bool


class PasswordGenerator:
    """Secure password generator with customizable options."""

    # Character sets
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    NUMBERS = string.digits
    SYMBOLS = '!@#$%^&*()_+-=[]{}|;:,.<>?'

    # Similar characters that can be excluded
    SIMILAR_CHARS = {
        '0': 'O',
        'O': '0',
        '1': 'lI',
        'l': '1I',
        'I': '1l',
        '5': 'S',
        'S': '5',
        '8': 'B',
        'B': '8'
    }

    # Ambiguous symbols
    AMBIGUOUS_SYMBOLS = '{}[]()/\\\'"`~,;:.<>'

    def __init__(self):
        self.exclude_similar = False
        self.exclude_ambiguous = False
        self.prevent_repeated = False
        self.prevent_sequential = False
        self.custom_charset = ''
        self.min_uppercase = 0
        self.min_lowercase = 0
        self.min_numbers = 0
        self.min_symbols = 0

    def _get_character_pool(self,
                            use_uppercase: bool = True,
                            use_lowercase: bool = True,
                            use_numbers: bool = True,
                            use_symbols: bool = True,
                            use_spaces: bool = False) -> Dict[str, str]:
        """Build character pools based on options."""
        pools = {}

        if use_uppercase:
            upper = self.UPPERCASE
            if self.exclude_similar:
                upper = ''.join(c for c in upper if c not in 'OISB')
            pools['uppercase'] = upper

        if use_lowercase:
            lower = self.LOWERCASE
            if self.exclude_similar:
                lower = ''.join(c for c in lower if c not in 'ol')
            pools['lowercase'] = lower

        if use_numbers:
            nums = self.NUMBERS
            if self.exclude_similar:
                nums = ''.join(c for c in nums if c not in '0185')
            pools['numbers'] = nums

        if use_symbols:
            syms = self.SYMBOLS
            if self.exclude_ambiguous:
                syms = ''.join(c for c in syms if c not in self.AMBIGUOUS_SYMBOLS)
            pools['symbols'] = syms

        if use_spaces:
            pools['spaces'] = ' '

        if self.custom_charset:
            pools['custom'] = self.custom_charset

        return pools

    def _is_sequential(self, char1: str, char2: str) -> bool:
        """Check if two characters are sequential."""
        if len(char1) != 1 or len(char2) != 1:
            return False

        # Check keyboard sequences
        keyboard_rows = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm',
            '1234567890'
        ]

        for row in keyboard_rows:
            for i in range(len(row) - 1):
                if (char1.lower() == row[i] and char2.lower() == row[i + 1]) or \
                   (char1.lower() == row[i + 1] and char2.lower() == row[i]):
                    return True

        # Check alphabetical sequence
        if char1.lower() in string.ascii_letters and char2.lower() in string.ascii_letters:
            idx1 = ord(char1.lower())
            idx2 = ord(char2.lower())
            if abs(idx1 - idx2) == 1:
                return True

        return False

    def generate(self,
                length: int = 16,
                use_uppercase: bool = True,
                use_lowercase: bool = True,
                use_numbers: bool = True,
                use_symbols: bool = True,
                use_spaces: bool = False) -> str:
        """
        Generate a cryptographically secure password.

        Args:
            length: Password length (4-128)
            use_uppercase: Include uppercase letters
            use_lowercase: Include lowercase letters
            use_numbers: Include numbers
            use_symbols: Include symbols
            use_spaces: Include spaces

        Returns:
            Generated password string
        """
        # Validate length
        length = max(4, min(128, length))

        # Get character pools
        pools = self._get_character_pool(
            use_uppercase, use_lowercase, use_numbers, use_symbols, use_spaces
        )

        if not pools:
            raise ValueError("At least one character type must be selected")

        # Combine all pools
        all_chars = ''.join(pools.values())

        if not all_chars:
            raise ValueError("Character pool is empty. Check exclusion settings.")

        password = []
        max_attempts = 1000
        attempts = 0

        while len(password) < length and attempts < max_attempts:
            attempts += 1
            char = secrets.choice(all_chars)

            # Check for repeated characters
            if self.prevent_repeated and password and char == password[-1]:
                continue

            # Check for sequential characters
            if self.prevent_sequential and password and self._is_sequential(password[-1], char):
                continue

            password.append(char)

        # Ensure minimum character requirements
        password = self._ensure_minimum_requirements(password, pools, length)

        # Shuffle the final password
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)

    def _ensure_minimum_requirements(self,
                                   password: List[str],
                                   pools: Dict[str, str],
                                   length: int) -> List[str]:
        """Ensure password meets minimum character type requirements."""
        password_str = ''.join(password)

        # Count current character types
        counts = {
            'uppercase': sum(1 for c in password_str if c in pools.get('uppercase', '')),
            'lowercase': sum(1 for c in password_str if c in pools.get('lowercase', '')),
            'numbers': sum(1 for c in password_str if c in pools.get('numbers', '')),
            'symbols': sum(1 for c in password_str if c in pools.get('symbols', ''))
        }

        # Replace characters if minimum requirements not met
        requirements = {
            'uppercase': self.min_uppercase,
            'lowercase': self.min_lowercase,
            'numbers': self.min_numbers,
            'symbols': self.min_symbols
        }

        for char_type, minimum in requirements.items():
            if minimum > 0 and char_type in pools and counts[char_type] < minimum:
                pool = pools[char_type]
                needed = minimum - counts[char_type]

                # Replace random positions with required character type
                positions_to_replace = []
                for _ in range(needed):
                    if len(password) < length:
                        password.append(secrets.choice(pool))
                    else:
                        # Find a position that's not already the required type
                        for i in range(len(password)):
                            if password[i] not in pool:
                                positions_to_replace.append(i)
                                break

                for pos in positions_to_replace[:needed]:
                    password[pos] = secrets.choice(pool)

        return password

    def generate_multiple(self,
                         count: int = 10,
                         length: int = 16,
                         use_uppercase: bool = True,
                         use_lowercase: bool = True,
                         use_numbers: bool = True,
                         use_symbols: bool = True) -> List[str]:
        """Generate multiple passwords at once."""
        passwords = []
        for _ in range(count):
            passwords.append(self.generate(
                length, use_uppercase, use_lowercase, use_numbers, use_symbols
            ))
        return passwords

    def generate_with_security_level(self, level: str) -> str:
        """
        Generate password based on predefined security level.

        Levels: Basic, Medium, Strong, Ultra Secure
        """
        configs = {
            'Basic': {'length': 10, 'uppercase': True, 'lowercase': True,
                     'numbers': True, 'symbols': False},
            'Medium': {'length': 14, 'uppercase': True, 'lowercase': True,
                      'numbers': True, 'symbols': False},
            'Strong': {'length': 20, 'uppercase': True, 'lowercase': True,
                      'numbers': True, 'symbols': True},
            'Ultra Secure': {'length': 32, 'uppercase': True, 'lowercase': True,
                           'numbers': True, 'symbols': True}
        }

        config = configs.get(level, configs['Strong'])
        return self.generate(
            length=config['length'],
            use_uppercase=config['uppercase'],
            use_lowercase=config['lowercase'],
            use_numbers=config['numbers'],
            use_symbols=config['symbols']
        )

    def analyze(self, password: str) -> PasswordAnalysis:
        """
        Analyze password strength and security.

        Returns detailed analysis including entropy, strength rating,
        estimated crack time, and security suggestions.
        """
        length = len(password)

        # Character type detection
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_numbers = bool(re.search(r'[0-9]', password))
        has_symbols = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password))
        has_spaces = ' ' in password

        # Calculate character pool size
        pool_size = 0
        if has_uppercase:
            pool_size += 26
        if has_lowercase:
            pool_size += 26
        if has_numbers:
            pool_size += 10
        if has_symbols:
            pool_size += 30
        if has_spaces:
            pool_size += 1

        # Calculate entropy
        if pool_size > 0 and length > 0:
            entropy = length * math.log2(pool_size)
        else:
            entropy = 0

        # Calculate strength score (0-100)
        strength_score = self._calculate_strength_score(
            length, has_uppercase, has_lowercase, has_numbers, has_symbols, entropy
        )

        # Determine strength level
        strength = self._get_strength_level(strength_score)

        # Estimate crack time
        crack_time = self._estimate_crack_time(entropy)

        # Generate suggestions
        suggestions = self._generate_suggestions(
            length, has_uppercase, has_lowercase, has_numbers, has_symbols
        )

        return PasswordAnalysis(
            length=length,
            entropy=round(entropy, 2),
            strength=strength,
            strength_score=strength_score,
            crack_time=crack_time,
            suggestions=suggestions,
            has_uppercase=has_uppercase,
            has_lowercase=has_lowercase,
            has_numbers=has_numbers,
            has_symbols=has_symbols
        )

    def _calculate_strength_score(self,
                                  length: int,
                                  has_upper: bool,
                                  has_lower: bool,
                                  has_numbers: bool,
                                  has_symbols: bool,
                                  entropy: float) -> int:
        """Calculate password strength score (0-100)."""
        score = 0

        # Length contribution (up to 25 points)
        length_score = min(25, length * 1.5)
        score += length_score

        # Character variety (up to 30 points)
        variety_count = sum([has_upper, has_lower, has_numbers, has_symbols])
        score += variety_count * 7.5

        # Entropy contribution (up to 45 points)
        entropy_score = min(45, entropy * 0.8)
        score += entropy_score

        return int(min(100, score))

    def _get_strength_level(self, score: int) -> str:
        """Convert score to strength level."""
        if score < 20:
            return 'Very Weak'
        elif score < 40:
            return 'Weak'
        elif score < 60:
            return 'Fair'
        elif score < 80:
            return 'Strong'
        else:
            return 'Very Strong'

    def _estimate_crack_time(self, entropy: float) -> str:
        """
        Estimate time to crack password based on entropy.
        Assumes 10 billion guesses per second (modern hardware).
        """
        if entropy <= 0:
            return 'Instant'

        guesses_per_second = 10_000_000_000  # 10 billion
        combinations = 2 ** entropy
        seconds = combinations / guesses_per_second / 2  # Average case

        if seconds < 1:
            return 'Less than a second'
        elif seconds < 60:
            return f'{int(seconds)} seconds'
        elif seconds < 3600:
            return f'{int(seconds / 60)} minutes'
        elif seconds < 86400:
            return f'{int(seconds / 3600)} hours'
        elif seconds < 31536000:
            return f'{int(seconds / 86400)} days'
        elif seconds < 31536000 * 100:
            return f'{int(seconds / 31536000)} years'
        elif seconds < 31536000 * 1000000:
            return f'{int(seconds / 31536000)} thousand years'
        elif seconds < 31536000 * 1000000000:
            return f'{int(seconds / 31536000)} million years'
        else:
            return 'Centuries+'

    def _generate_suggestions(self,
                             length: int,
                             has_upper: bool,
                             has_lower: bool,
                             has_numbers: bool,
                             has_symbols: bool) -> List[str]:
        """Generate security improvement suggestions."""
        suggestions = []

        if length < 8:
            suggestions.append('Increase length to at least 8 characters')
        elif length < 12:
            suggestions.append('Consider using 12+ characters for better security')
        elif length < 16:
            suggestions.append('16+ characters recommended for high security')

        if not has_upper:
            suggestions.append('Add uppercase letters (A-Z)')
        if not has_lower:
            suggestions.append('Add lowercase letters (a-z)')
        if not has_numbers:
            suggestions.append('Add numbers (0-9)')
        if not has_symbols:
            suggestions.append('Add symbols (!@#$%^&*) for maximum security')

        # Variety suggestion
        variety = sum([has_upper, has_lower, has_numbers, has_symbols])
        if variety < 4:
            suggestions.append(f'Use all character types for maximum entropy')

        return suggestions


def get_security_level_description(level: str) -> Dict:
    """Get configuration for a security level."""
    descriptions = {
        'Basic': {
            'length_range': (8, 10),
            'description': 'Letters and numbers only. Good for basic accounts.',
            'character_types': 'Uppercase, Lowercase, Numbers'
        },
        'Medium': {
            'length_range': (12, 16),
            'description': 'Mixed case letters and numbers. Suitable for most accounts.',
            'character_types': 'Uppercase, Lowercase, Numbers'
        },
        'Strong': {
            'length_range': (16, 24),
            'description': 'Full character set. Recommended for sensitive accounts.',
            'character_types': 'Uppercase, Lowercase, Numbers, Symbols'
        },
        'Ultra Secure': {
            'length_range': (24, 64),
            'description': 'Maximum entropy. Use for critical security.',
            'character_types': 'All character types, maximum complexity'
        }
    }
    return descriptions.get(level, descriptions['Strong'])
