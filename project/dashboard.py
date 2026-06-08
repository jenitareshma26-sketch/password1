"""
Dashboard module for analytics and visualizations.
"""

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, List
from database import Database
from settings import ThemeManager
import pandas as pd
import tkinter as tk


class DashboardManager:
    """Manager for dashboard analytics and visualizations."""

    def __init__(self, db: Database = None, theme_manager: ThemeManager = None):
        self.db = db if db else Database()
        self.theme_manager = theme_manager
        self._figure = None
        self._canvas = None

    def get_statistics(self) -> Dict:
        """Get current statistics data."""
        return self.db.get_statistics()

    def create_strength_pie_chart(self, parent: tk.Widget) -> FigureCanvasTkAgg:
        """Create password strength distribution pie chart."""
        stats = self.get_statistics()
        strength_data = stats['strength_distribution']

        if not strength_data:
            strength_data = {'No Data': 1}

        colors = self._get_theme_colors()

        fig = Figure(figsize=(6, 4), dpi=100, facecolor=colors['bg_secondary'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(colors['bg_secondary'])

        labels = list(strength_data.keys())
        sizes = list(strength_data.values())

        pie_colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#10b981']
        if len(labels) <= 5:
            used_colors = [pie_colors[i] for i in range(len(labels))]
        else:
            used_colors = pie_colors * (len(labels) // 5 + 1)

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            colors=used_colors[:len(labels)],
            textprops={'color': colors['text_primary']}
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Password Strength Distribution',
                    color=colors['text_primary'], fontsize=14)

        fig.tight_layout()

        self._figure = fig
        self._canvas = FigureCanvasTkAgg(fig, master=parent)
        self._canvas.draw()

        return self._canvas

    def create_length_bar_chart(self, parent: tk.Widget) -> FigureCanvasTkAgg:
        """Create password length analysis bar chart."""
        passwords = self.db.get_all_passwords()

        if not passwords:
            lengths = {'0-8': 0, '9-12': 0, '13-16': 0, '17-24': 0, '24+': 0}
        else:
            lengths = {
                '4-8': 0,
                '9-12': 0,
                '13-16': 0,
                '17-24': 0,
                '24+': 0
            }

            for p in passwords:
                length = p['length']
                if length <= 8:
                    lengths['4-8'] += 1
                elif length <= 12:
                    lengths['9-12'] += 1
                elif length <= 16:
                    lengths['13-16'] += 1
                elif length <= 24:
                    lengths['17-24'] += 1
                else:
                    lengths['24+'] += 1

        colors = self._get_theme_colors()

        fig = Figure(figsize=(6, 4), dpi=100, facecolor=colors['bg_secondary'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(colors['bg_secondary'])

        x_labels = list(lengths.keys())
        y_values = list(lengths.values())

        bars = ax.bar(x_labels, y_values,
                     color=colors['accent_primary'],
                     edgecolor=colors['border'])

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       ha='center', va='bottom',
                       color=colors['text_primary'])

        ax.set_xlabel('Password Length Range', color=colors['text_primary'])
        ax.set_ylabel('Count', color=colors['text_primary'])
        ax.set_title('Password Length Distribution',
                    color=colors['text_primary'], fontsize=14)

        ax.tick_params(colors=colors['text_primary'])
        ax.spines['bottom'].set_color(colors['border'])
        ax.spines['top'].set_color(colors['border'])
        ax.spines['left'].set_color(colors['border'])
        ax.spines['right'].set_color(colors['border'])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()

        return canvas

    def create_generation_trend_chart(self, parent: tk.Widget) -> FigureCanvasTkAgg:
        """Create generation trend line chart."""
        stats = self.get_statistics()
        trend_data = stats['trend_data']

        colors = self._get_theme_colors()

        fig = Figure(figsize=(6, 4), dpi=100, facecolor=colors['bg_secondary'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(colors['bg_secondary'])

        if trend_data:
            dates = list(trend_data.keys())
            counts = list(trend_data.values())

            ax.plot(dates, counts, marker='o',
                   color=colors['accent_primary'],
                   linewidth=2, markersize=8)

            ax.fill_between(dates, counts, alpha=0.3, color=colors['accent_primary'])
        else:
            ax.text(0.5, 0.5, 'No recent data',
                   ha='center', va='center',
                   color=colors['text_muted'])

        ax.set_xlabel('Date', color=colors['text_primary'])
        ax.set_ylabel('Passwords Generated', color=colors['text_primary'])
        ax.set_title('Generation Trend (Last 7 Days)',
                    color=colors['text_primary'], fontsize=14)

        ax.tick_params(colors=colors['text_primary'])
        for spine in ax.spines.values():
            spine.set_color(colors['border'])

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()

        return canvas

    def create_entropy_chart(self, parent: tk.Widget) -> FigureCanvasTkAgg:
        """Create entropy distribution chart."""
        passwords = self.db.get_all_passwords()

        colors = self._get_theme_colors()

        fig = Figure(figsize=(6, 4), dpi=100, facecolor=colors['bg_secondary'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(colors['bg_secondary'])

        if passwords:
            entropy_values = [p.get('entropy', 0) for p in passwords if p.get('entropy')]
            generations = range(1, len(entropy_values) + 1)

            ax.scatter(generations, entropy_values,
                      c=colors['accent_secondary'],
                      alpha=0.6, s=50)

            if len(entropy_values) > 1:
                ax.plot(generations, entropy_values,
                       color=colors['accent_primary'],
                       alpha=0.3, linewidth=1)
        else:
            ax.text(0.5, 0.5, 'No data available',
                   ha='center', va='center',
                   color=colors['text_muted'])

        ax.set_xlabel('Generation #', color=colors['text_primary'])
        ax.set_ylabel('Entropy (bits)', color=colors['text_primary'])
        ax.set_title('Password Entropy Over Time',
                    color=colors['text_primary'], fontsize=14)

        ax.tick_params(colors=colors['text_primary'])
        for spine in ax.spines.values():
            spine.set_color(colors['border'])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()

        return canvas

    def _get_theme_colors(self) -> Dict:
        """Get current theme colors for charts."""
        if self.theme_manager:
            return self.theme_manager.get_theme()
        return ThemeManager.DARK_THEME

    def refresh_all_charts(self, parent: tk.Widget) -> Dict[str, FigureCanvasTkAgg]:
        """Refresh all dashboard charts."""
        return {
            'pie': self.create_strength_pie_chart(parent),
            'bar': self.create_length_bar_chart(parent),
            'trend': self.create_generation_trend_chart(parent),
            'entropy': self.create_entropy_chart(parent)
        }

    def get_summary_stats(self) -> Dict:
        """Get summary statistics for display."""
        stats = self.get_statistics()

        total = stats['total_generated']
        avg_length = stats['average_length']
        avg_entropy = stats['average_entropy']
        strength_dist = stats['strength_distribution']

        strong_count = strength_dist.get('Strong', 0) + strength_dist.get('Very Strong', 0)
        strong_percentage = (strong_count / total * 100) if total > 0 else 0

        return {
            'total_passwords': total,
            'average_length': avg_length,
            'average_entropy': avg_entropy,
            'strong_password_percentage': round(strong_percentage, 1),
            'strength_distribution': strength_dist
        }

    def export_stats_to_dict(self) -> Dict:
        """Export statistics as dictionary for reports."""
        stats = self.get_summary_stats()
        passwords = self.db.get_all_passwords()

        # Calculate additional metrics
        lengths = [p['length'] for p in passwords]
        entropies = [p.get('entropy', 0) for p in passwords]

        return {
            'total_passwords_generated': stats['total_passwords'],
            'average_password_length': stats['average_length'],
            'minimum_length': min(lengths) if lengths else 0,
            'maximum_length': max(lengths) if lengths else 0,
            'average_entropy': stats['average_entropy'],
            'strong_password_rate': f"{stats['strong_password_percentage']}%",
            'strength_distribution': stats['strength_distribution'],
            'history_count': len(passwords)
        }

    def cleanup(self):
        """Clean up matplotlib resources."""
        plt.close('all')
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
        if self._figure:
            self._figure.clear()
