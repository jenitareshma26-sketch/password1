"""
Reports module for exporting password data in various formats.
"""

import os
import csv
from datetime import datetime
from typing import List, Dict
import pandas as pd

from database import Database
from utils import ensure_directory, generate_filename, get_export_path
from dashboard import DashboardManager


class ReportExporter:
    """Export passwords and statistics in various formats."""

    def __init__(self, db: Database = None, export_dir: str = 'exports'):
        self.db = db if db else Database()
        self.export_dir = export_dir
        self.dashboard = DashboardManager(db)
        ensure_directory(export_dir)

    def export_to_txt(self, passwords: List[Dict], filename: str = None) -> str:
        """
        Export passwords to a text file.

        Returns the file path on success.
        """
        if not filename:
            filename = generate_filename('passwords', 'txt')

        filepath = get_export_path(filename, self.export_dir)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("PASSWORD EXPORT REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                for i, p in enumerate(passwords, 1):
                    f.write(f"Password #{i}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Password: {p.get('password', 'N/A')}\n")
                    f.write(f"Strength: {p.get('strength', 'N/A')}\n")
                    f.write(f"Length: {p.get('length', 'N/A')}\n")
                    if p.get('entropy'):
                        f.write(f"Entropy: {p['entropy']:.2f} bits\n")
                    f.write(f"Created: {p.get('created_at', 'N/A')}\n")
                    f.write("\n")

                f.write("=" * 60 + "\n")
                f.write(f"Total passwords: {len(passwords)}\n")

            return filepath

        except Exception as e:
            raise RuntimeError(f"Failed to export to TXT: {str(e)}")

    def export_to_csv(self, passwords: List[Dict], filename: str = None) -> str:
        """
        Export passwords to CSV format.

        Returns the file path on success.
        """
        if not filename:
            filename = generate_filename('passwords', 'csv')

        filepath = get_export_path(filename, self.export_dir)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['Password', 'Strength', 'Length', 'Entropy', 'Created At'])

                # Data
                for p in passwords:
                    writer.writerow([
                        p.get('password', ''),
                        p.get('strength', ''),
                        p.get('length', ''),
                        f"{p.get('entropy', 0):.2f}" if p.get('entropy') else '',
                        p.get('created_at', '')
                    ])

            return filepath

        except Exception as e:
            raise RuntimeError(f"Failed to export to CSV: {str(e)}")

    def export_to_excel(self, passwords: List[Dict], filename: str = None) -> str:
        """
        Export passwords to Excel format.

        Returns the file path on success.
        """
        if not filename:
            filename = generate_filename('passwords', 'xlsx')

        filepath = get_export_path(filename, self.export_dir)

        try:
            # Create DataFrame
            df = pd.DataFrame(passwords)

            if not df.empty:
                # Rename columns for better display
                df = df[['password', 'strength', 'length', 'entropy', 'created_at']]
                df.columns = ['Password', 'Strength', 'Length', 'Entropy (bits)', 'Created At']

            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main password sheet
                df.to_excel(writer, sheet_name='Passwords', index=False)

                # Statistics sheet
                stats = self.dashboard.get_summary_stats()
                stats_df = pd.DataFrame([
                    ['Total Passwords', stats['total_passwords']],
                    ['Average Length', stats['average_length']],
                    ['Average Entropy', stats['average_entropy']],
                    ['Strong Password Rate', f"{stats['strong_password_percentage']}%"]
                ], columns=['Metric', 'Value'])
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)

                # Strength distribution sheet
                strength_data = []
                for strength, count in stats['strength_distribution'].items():
                    strength_data.append([strength, count])
                strength_df = pd.DataFrame(strength_data, columns=['Strength Level', 'Count'])
                strength_df.to_excel(writer, sheet_name='Strength Distribution', index=False)

            return filepath

        except Exception as e:
            raise RuntimeError(f"Failed to export to Excel: {str(e)}")

    def export_to_pdf(self, passwords: List[Dict], filename: str = None) -> str:
        """
        Export passwords to PDF format.

        Returns the file path on success.
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER

        if not filename:
            filename = generate_filename('passwords', 'pdf')

        filepath = get_export_path(filename, self.export_dir)

        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch
            )

            elements = []

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                alignment=TA_CENTER,
                spaceAfter=12,
                textColor=colors.Color(0.4, 0.4, 0.95)
            )
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=colors.gray
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.Color(0.15, 0.15, 0.15)
            )

            # Title
            elements.append(Paragraph("Password Export Report", title_style))
            elements.append(Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                subtitle_style
            ))
            elements.append(Spacer(1, 20))

            # Statistics summary
            stats = self.dashboard.get_summary_stats()

            elements.append(Paragraph("Summary Statistics", heading_style))
            elements.append(Spacer(1, 10))

            summary_data = [
                ['Metric', 'Value'],
                ['Total Passwords Exported', str(len(passwords))],
                ['Average Password Length', f"{stats['average_length']} characters"],
                ['Average Entropy', f"{stats['average_entropy']:.2f} bits"],
                ['Strong Password Rate', f"{stats['strong_password_percentage']}%"]
            ]

            summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.15, 0.15, 0.35)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.96, 0.96, 0.98)),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(0.15, 0.15, 0.15)),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.85)),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(summary_table)
            elements.append(Spacer(1, 30))

            # Strength distribution
            elements.append(Paragraph("Strength Distribution", heading_style))
            elements.append(Spacer(1, 10))

            strength_data = [['Strength Level', 'Count', 'Percentage']]
            total = len(passwords) if passwords else 1

            for strength, count in stats['strength_distribution'].items():
                percentage = f"{(count / total * 100):.1f}%"
                strength_data.append([strength, str(count), percentage])

            if not stats['strength_distribution']:
                strength_data.append(['No data', '0', '0%'])

            strength_table = Table(strength_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
            strength_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.3, 0.15, 0.35)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.97, 0.97, 0.99)),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(0.2, 0.2, 0.2)),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.85, 0.85, 0.9)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))

            elements.append(strength_table)
            elements.append(PageBreak())

            # Password list
            elements.append(Paragraph("Password List", heading_style))
            elements.append(Spacer(1, 10))

            # Prepare password table data
            password_data = [['#', 'Password', 'Strength', 'Length', 'Created']]
            for i, p in enumerate(passwords[:50], 1):
                pwd = p.get('password', '')
                if len(pwd) > 25:
                    pwd = pwd[:22] + '...'
                password_data.append([
                    str(i),
                    pwd,
                    p.get('strength', 'N/A'),
                    str(p.get('length', 'N/A')),
                    p.get('created_at', 'N/A')[:10] if p.get('created_at') else ''
                ])

            # Create password table
            col_widths = [0.3 * inch, 3 * inch, 1.2 * inch, 0.6 * inch, 1.5 * inch]
            password_table = Table(password_data, colWidths=col_widths)

            # Define strength colors
            def get_strength_color(strength):
                colors_map = {
                    'Very Strong': colors.Color(0.13, 0.83, 0.27),
                    'Strong': colors.Color(0.53, 0.8, 0.27),
                    'Fair': colors.Color(0.92, 0.7, 0.03),
                    'Weak': colors.Color(1.0, 0.53, 0.27),
                    'Very Weak': colors.Color(0.94, 0.27, 0.27)
                }
                return colors_map.get(strength, colors.gray)

            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.15, 0.15, 0.35)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.85)),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 1), (3, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]

            # Add row backgrounds
            for i, p in enumerate(passwords[:50], 1):
                bg_color = colors.Color(0.97, 0.97, 0.99) if i % 2 == 0 else colors.white
                table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))

                # Color-code strength column
                strength = p.get('strength', '')
                strength_color = get_strength_color(strength)
                table_style.append(('TEXTCOLOR', (2, i), (2, i), strength_color))
                table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))

            password_table.setStyle(TableStyle(table_style))
            elements.append(password_table)

            if len(passwords) > 50:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(
                    f"... and {len(passwords) - 50} more passwords",
                    styles['Normal']
                ))

            # Footer
            elements.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.gray
            )
            elements.append(Paragraph(
                "Generated by Advanced Password Generator | Secure Password Management",
                footer_style
            ))

            # Build PDF
            doc.build(elements)

            return filepath

        except Exception as e:
            raise RuntimeError(f"Failed to export to PDF: {str(e)}")

    def export_bulk_passwords(self, passwords: List[str], format: str = 'txt') -> str:
        """Export bulk generated passwords (list of strings)."""
        password_dicts = [
            {'password': p, 'strength': '', 'length': len(p)}
            for p in passwords
        ]
        return self.export(password_dicts, format)

    def export(self, passwords: List[Dict], format: str = 'txt') -> str:
        """
        Export passwords in specified format.

        Args:
            passwords: List of password dictionaries
            format: Export format ('txt', 'csv', 'xlsx', 'pdf')

        Returns:
            File path of exported file
        """
        exporters = {
            'txt': self.export_to_txt,
            'csv': self.export_to_csv,
            'xlsx': self.export_to_excel,
            'pdf': self.export_to_pdf,
            'excel': self.export_to_excel
        }

        exporter = exporters.get(format.lower())
        if not exporter:
            raise ValueError(f"Unsupported format: {format}")

        return exporter(passwords)

    def export_history(self, format: str = 'txt') -> str:
        """Export all password history."""
        passwords = self.db.get_all_passwords()
        return self.export(passwords, format)

    def get_export_directory(self) -> str:
        """Get the current export directory path."""
        return os.path.abspath(self.export_dir)

    def set_export_directory(self, path: str) -> bool:
        """Set a new export directory."""
        try:
            if ensure_directory(path):
                self.export_dir = path
                return True
            return False
        except Exception:
            return False
