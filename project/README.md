# Advanced Random Password Generator

A professional desktop application for generating secure, cryptographically strong passwords with a modern UI.

## Features

### Password Generation
- Customizable length (4-128 characters)
- Character type selection (uppercase, lowercase, numbers, symbols, spaces)
- Cryptographically secure generation using `secrets` module
- Predefined security levels (Basic, Medium, Strong, Ultra Secure)

### Security Analysis
- Real-time entropy calculation
- Strength scoring (0-100)
- Estimated crack time
- Security suggestions

### Password History
- SQLite database storage
- Search functionality
- Export capabilities

### Dashboard & Analytics
- Password strength distribution (pie chart)
- Length analysis (bar chart)
- Generation trends (line chart)
- Entropy visualization

### Export Options
- TXT format
- CSV format
- Excel (.xlsx)
- PDF reports

### Advanced Options
- Exclude similar characters (0/O, 1/l/I)
- Exclude ambiguous symbols
- Prevent repeated characters
- Prevent sequential characters
- Minimum character requirements

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python3 main.py
```

## Project Structure

```
Password_Generator/
├── main.py              # Main application entry point
├── password_generator.py # Password generation logic
├── database.py          # SQLite database operations
├── dashboard.py         # Analytics and charts
├── reports.py           # Export functionality
├── utils.py             # Helper functions
├── settings.py          # Configuration management
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
├── database/            # SQLite database files
├── exports/              # Exported files
└── assets/              # Application assets
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+G | Generate new password |
| Ctrl+C | Copy current password |
| Ctrl+R | Regenerate password |
| Ctrl+T | Toggle theme |
| F1 | Show help |
| Escape | Exit application |

## Security Levels

| Level | Length | Characters |
|-------|--------|------------|
| Basic | 8-10 | Letters, numbers |
| Medium | 12-16 | Uppercase, lowercase, numbers |
| Strong | 16-24 | All types including symbols |
| Ultra Secure | 24-64 | Maximum complexity |

## License

This project is provided as-is for educational and personal use.
