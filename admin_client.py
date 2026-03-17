"""
Randevu Sistemi - Admin Client Pro
Professional Appointment Management with Real-time Updates
"""
import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QDialog, QTextEdit, QMessageBox, QLineEdit, QStackedWidget,
    QScrollArea, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QFontDatabase, QIcon

from database import get_db, Appointment, AppointmentStatus
from sound_manager import get_sound_manager
from config import AppConfig

# ============================================================
# STYLES
# ============================================================
ADMIN_STYLES = f"""
QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
}}

QWidget {{
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.card {{
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}}

.card:hover {{
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
}}

.stat-card {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(99, 102, 241, 0.3), stop:1 rgba(139, 92, 246, 0.1));
    border-radius: 20px;
    border: 1px solid rgba(99, 102, 241, 0.3);
    padding: 20px;
}}

.stat-card.pending {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(245, 158, 11, 0.3), stop:1 rgba(251, 191, 36, 0.1));
    border: 1px solid rgba(245, 158, 11, 0.3);
}}

.stat-card.accepted {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(16, 185, 129, 0.3), stop:1 rgba(52, 211, 153, 0.1));
    border: 1px solid rgba(16, 185, 129, 0.3);
}}

.stat-card.rejected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(239, 68, 68, 0.3), stop:1 rgba(248, 113, 113, 0.1));
    border: 1px solid rgba(239, 68, 68, 0.3);
}}

.action-btn {{
    background-color: {AppConfig.INFO_COLOR};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
    min-width: 35px;
}}

.action-btn:hover {{
    background-color: #6366f1;
    transform: scale(1.05);
}}

.action-btn.accept {{
    background-color: {AppConfig.SUCCESS_COLOR};
}}

.action-btn.accept:hover {{
    background-color: #059669;
}}

.action-btn.reject {{
    background-color: {AppConfig.DANGER_COLOR};
}}

.action-btn.reject:hover {{
    background-color: #dc2626;
}}

.action-btn.delete {{
    background-color: rgba(255,255,255,0.1);
    color: #9ca3af;
}}

.action-btn.delete:hover {{
    background-color: {AppConfig.DANGER_COLOR};
    color: white;
}}

QTableWidget {{
    background-color: transparent;
    border: none;
    color: white;
    font-size: 13px;
    gridline-color: rgba(255,255,255,0.05);
}}

QTableWidget::item {{
    padding: 15px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}

QTableWidget::item:selected {{
    background-color: rgba(99, 102, 241, 0.2);
}}

QHeaderView::section {{
    background-color: rgba(255,255,255,0.05);
    color: #9ca3af;
    padding: 15px 10px;
    border: none;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:first {{
    border-radius: 10px 0 0 0;
}}

QHeaderView::section:last {{
    border-radius: 0 10px 0 0;
}}

QLineEdit, QTextEdit {{
    background-color: rgba(255,255,255,0.05);
    color: white;
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: #6366f1;
    background-color: rgba(255,255,255,0.08);
}}

QPushButton.nav-btn {{
    background-color: transparent;
    color: #9ca3af;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
}}

QPushButton.nav-btn:hover {{
    background-color: rgba(255,255,255,0.05);
    color: white;
}}

QPushButton.nav-btn.active {{
    background-color: rgba(99, 102, 241, 0.2);
    color: #818cf8;
    border-left: 3px solid #818cf8;
}}

QLabel.badge {{
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel.badge-pending {{
    background-color: rgba(245, 158, 11, 0.2);
    color: #fbbf24;
}}

QLabel.badge-accepted {{
    background-color: rgba(16, 185, 129, 0.2);
    color: #34d399;
}}

QLabel.badge-rejected {{
    background-color: rgba(239, 68, 68, 0.2);
    color: #f87171;
}}
"""

# ============================================================
# WIDGETS
# ============================================================

class AnimatedButton(QPushButton):
    """Button with smooth hover animation"""
    def __init__(self, text, color="#6366f1", parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.sound = get_sound_manager()
        self._setup_style()
        
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _setup_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: white;
                border: none;
                border-radius: 14px;
                padding: 14px 28px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #818cf8;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        self.sound.play_button()
        super().enterEvent(event)
    
    def mousePressEvent(self, event):
        self.sound.play_tap()
        super().mousePressEvent(event)


class StatCard(QFrame):
    """Professional stat card with gradient"""
    def __init__(self, title, value, icon, card_class="", color="#6366f1", parent=None):
        super().__init__(parent)
        self.setProperty("class", f"stat-card {card_class}")
        self.setStyleSheet(ADMIN_STYLES)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 32px; margin-bottom: 5px;")
        layout.addWidget(icon_lbl)
        
        # Value
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 42px;
            font-weight: 800;
        """)
        layout.addWidget(self.value_lbl)
        
        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #9ca3af; font-size: 13px; font-weight: 500;")
        layout.addWidget(title_lbl)
    
    def set_value(self, value):
        self.value_lbl.setText(str(value))


class AppointmentRow(QWidget):
    """Custom appointment row widget"""
    accept_clicked = pyqtSignal(int)
    reject_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    view_clicked = pyqtSignal(object)
    
    def __init__(self, appointment: Appointment, parent=None):
        super().__init__(parent)
        self.appointment = appointment
        self.sound = get_sound_manager()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        # Queue number
        queue = QLabel(f"#{self.appointment.queue_number}")
        queue.setStyleSheet("""
            font-size: 18px;
            font-weight: 800;
            color: #818cf8;
            min-width: 50px;
        """)
        layout.addWidget(queue)
        
        # Status badge
        status_text = self.appointment.status.value
        if self.appointment.status == AppointmentStatus.PENDING:
            badge_class = "badge-pending"
            badge_text = "⏳ " + status_text
        elif self.appointment.status == AppointmentStatus.ACCEPTED:
            badge_class = "badge-accepted"
            badge_text = "✅ " + status_text
        else:
            badge_class = "badge-rejected"
            badge_text = "❌ " + status_text
        
        badge = QLabel(badge_text)
        badge.setProperty("class", f"badge {badge_class}")
        badge.setStyleSheet(ADMIN_STYLES)
        badge.setMinimumWidth(120)
        layout.addWidget(badge)
        
        # Note
        note_text = self.appointment.note[:30] + "..." if len(self.appointment.note) > 30 else self.appointment.note
        note = QLabel(note_text or "—")
        note.setStyleSheet("color: #d1d5db; font-size: 13px;")
        note.setMinimumWidth(200)
        layout.addWidget(note, stretch=1)
        
        # Time
        time_str = self.appointment.created_at.strftime("%H:%M")
        time_lbl = QLabel(f"🕐 {time_str}")
        time_lbl.setStyleSheet("color: #6b7280; font-size: 12px; min-width: 70px;")
        layout.addWidget(time_lbl)
        
        # Actions
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)
        
        # View button
        view_btn = QPushButton("👁️")
        view_btn.setProperty("class", "action-btn")
        view_btn.setStyleSheet(ADMIN_STYLES)
        view_btn.setToolTip("Detay")
        view_btn.clicked.connect(lambda: self.view_clicked.emit(self.appointment))
        btn_layout.addWidget(view_btn)
        
        # Accept/Reject for pending
        if self.appointment.status == AppointmentStatus.PENDING:
            accept_btn = QPushButton("✓")
            accept_btn.setProperty("class", "action-btn accept")
            accept_btn.setStyleSheet(ADMIN_STYLES)
            accept_btn.setToolTip("Kabul Et")
            accept_btn.clicked.connect(lambda: self.accept_clicked.emit(self.appointment.id))
            btn_layout.addWidget(accept_btn)
            
            reject_btn = QPushButton("✕")
            reject_btn.setProperty("class", "action-btn reject")
            reject_btn.setStyleSheet(ADMIN_STYLES)
            reject_btn.setToolTip("Reddet")
            reject_btn.clicked.connect(lambda: self.reject_clicked.emit(self.appointment.id))
            btn_layout.addWidget(reject_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setProperty("class", "action-btn delete")
        delete_btn.setStyleSheet(ADMIN_STYLES)
        delete_btn.setToolTip("Sil")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.appointment.id))
        btn_layout.addWidget(delete_btn)
        
        layout.addWidget(btn_container)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255,255,255,0.03);
                border-radius: 12px;
            }
            QWidget:hover {
                background-color: rgba(255,255,255,0.06);
            }
        """)


class SettingsDialog(QDialog):
    """Professional settings dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Sistem Ayarları")
        self.setMinimumSize(500, 400)
        self.sound = get_sound_manager()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🔧 Supabase Yapılandırması")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #818cf8;")
        layout.addWidget(header)
        
        # Card
        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet(ADMIN_STYLES)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # URL
        url_lbl = QLabel("🔌 Supabase URL")
        url_lbl.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: 600;")
        card_layout.addWidget(url_lbl)
        
        self.url_input = QLineEdit(AppConfig.SUPABASE_URL)
        self.url_input.setPlaceholderText("https://your-project.supabase.co")
        card_layout.addWidget(self.url_input)
        
        # Key
        key_lbl = QLabel("🔑 Supabase Anon Key")
        key_lbl.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: 600;")
        card_layout.addWidget(key_lbl)
        
        self.key_input = QLineEdit(AppConfig.SUPABASE_KEY)
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("eyJhbGciOiJIUzI1NiIs...")
        card_layout.addWidget(self.key_input)
        
        # Show/Hide
        show_btn = QPushButton("👁️ Key Göster")
        show_btn.setCheckable(True)
        show_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.1);
                color: #9ca3af;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        show_btn.toggled.connect(self._toggle_key)
        card_layout.addWidget(show_btn)
        
        layout.addWidget(card)
        
        # Path info
        path_lbl = QLabel(f"💾 Kaydedilecek: {AppConfig.get_env_path()}")
        path_lbl.setStyleSheet("color: #6b7280; font-size: 11px;")
        path_lbl.setWordWrap(True)
        layout.addWidget(path_lbl)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        test_btn = AnimatedButton("🔗 Bağlantı Testi", "#3b82f6")
        test_btn.clicked.connect(self._test_connection)
        btn_layout.addWidget(test_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = AnimatedButton("İptal", "#374151")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = AnimatedButton("💾 Kaydet", "#10b981")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
        """)
    
    def _toggle_key(self, checked):
        self.key_input.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
    
    def _test_connection(self):
        import requests
        try:
            headers = {"apikey": self.key_input.text(), "Authorization": f"Bearer {self.key_input.text()}"}
            r = requests.get(f"{self.url_input.text()}/rest/v1/", headers=headers, timeout=5)
            if r.status_code == 200:
                QMessageBox.information(self, "✅ Başarılı", "Supabase bağlantısı aktif!")
            else:
                QMessageBox.warning(self, "⚠️ Hata", f"Sunucu yanıtı: {r.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Bağlantı Hatası", str(e))
    
    def _save(self):
        AppConfig.save_env(self.url_input.text(), self.key_input.text())
        QMessageBox.information(self, "✅ Kaydedildi", "Değişiklikler kaydedildi!\nProgramı yeniden başlatın.")
        self.accept()


# ============================================================
# MAIN ADMIN CLIENT
# ============================================================

class AdminClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = get_db()
        self.sound = get_sound_manager()
        self.current_filter = "all"
        self.last_total = 0
        self.last_pending = 0
        self.appointment_rows = []
        self.sort_descending = True  # True = Yeni → Eski, False = Eski → Yeni
        
        self.setWindowTitle(f"{AppConfig.APP_NAME} - Admin Dashboard")
        self.setMinimumSize(1400, 900)
        
        self.setup_ui()
        self.apply_styles()
        
        # Auto refresh timer - every 3 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(3000)
        
        # Initial load
        QTimer.singleShot(500, self._load_data)
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content = self._create_content()
        main_layout.addWidget(content, stretch=1)
    
    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setMaximumWidth(250)
        sidebar.setStyleSheet("""
            background-color: rgba(0,0,0,0.2);
            border-right: 1px solid rgba(255,255,255,0.05);
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Logo
        logo = QLabel("🗓️")
        logo.setStyleSheet("font-size: 40px;")
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Randevu Pro")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel(f"v{AppConfig.APP_VERSION}")
        version.setStyleSheet("color: #6b7280; font-size: 11px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(30)
        
        # Nav buttons
        self.nav_all = self._create_nav_btn("📋 Tüm Randevular", True)
        self.nav_pending = self._create_nav_btn("⏳ Bekleyenler")
        self.nav_accepted = self._create_nav_btn("✅ Kabul Edilenler")
        self.nav_rejected = self._create_nav_btn("❌ Reddedilenler")
        
        layout.addWidget(self.nav_all)
        layout.addWidget(self.nav_pending)
        layout.addWidget(self.nav_accepted)
        layout.addWidget(self.nav_rejected)
        
        layout.addStretch()
        
        # Settings
        settings_btn = self._create_nav_btn("⚙️ Ayarlar")
        settings_btn.clicked.connect(lambda: SettingsDialog(self).exec())
        layout.addWidget(settings_btn)
        
        return sidebar
    
    def _create_nav_btn(self, text, active=False) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "nav-btn active" if active else "nav-btn")
        btn.setStyleSheet(ADMIN_STYLES)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Set filter on click
        if "Tüm" in text:
            btn.clicked.connect(lambda: self._set_filter("all"))
        elif "Bekleyen" in text:
            btn.clicked.connect(lambda: self._set_filter("pending"))
        elif "Kabul" in text:
            btn.clicked.connect(lambda: self._set_filter("accepted"))
        elif "Red" in text:
            btn.clicked.connect(lambda: self._set_filter("rejected"))
        
        return btn
    
    def _create_content(self) -> QWidget:
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        welcome = QLabel("👋 Hoş Geldiniz")
        welcome.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        header_layout.addWidget(welcome)
        
        header_layout.addStretch()
        
        # Auto refresh indicator
        self.refresh_indicator = QLabel("🔄 Canlı")
        self.refresh_indicator.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        """)
        header_layout.addWidget(self.refresh_indicator)
        
        layout.addWidget(header)
        
        # Stats grid
        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        self.stat_total = StatCard("Toplam Randevu", "0", "📊", "", "#818cf8")
        self.stat_pending = StatCard("Bekleyen", "0", "⏳", "pending", "#fbbf24")
        self.stat_accepted = StatCard("Kabul Edilen", "0", "✅", "accepted", "#34d399")
        self.stat_rejected = StatCard("Reddedilen", "0", "❌", "rejected", "#f87171")
        
        stats_layout.addWidget(self.stat_total, 0, 0)
        stats_layout.addWidget(self.stat_pending, 0, 1)
        stats_layout.addWidget(self.stat_accepted, 0, 2)
        stats_layout.addWidget(self.stat_rejected, 0, 3)
        
        layout.addWidget(stats_widget)
        
        # Appointments section
        section_header = QWidget()
        section_layout = QHBoxLayout(section_header)
        section_layout.setContentsMargins(0, 0, 0, 0)
        
        section_title = QLabel("📋 Randevu Listesi")
        section_title.setStyleSheet("font-size: 20px; font-weight: 600; color: white;")
        section_layout.addWidget(section_title)
        
        section_layout.addStretch()
        
        # Sort toggle button
        self.sort_btn = AnimatedButton("↓ Yeniden Eskiye", "#6366f1")
        self.sort_btn.setToolTip("Sıralama değiştirmek için tıklayın")
        self.sort_btn.clicked.connect(self._toggle_sort)
        section_layout.addWidget(self.sort_btn)
        
        # Filter label
        self.filter_lbl = QLabel("Tümü")
        self.filter_lbl.setStyleSheet("color: #9ca3af; font-size: 13px;")
        section_layout.addWidget(self.filter_lbl)
        
        refresh_btn = AnimatedButton("🔄 Yenile", "#3b82f6")
        refresh_btn.clicked.connect(self._load_data)
        section_layout.addWidget(refresh_btn)
        
        layout.addWidget(section_header)
        
        # Table container
        table_container = QFrame()
        table_container.setProperty("class", "card")
        table_container.setStyleSheet(ADMIN_STYLES)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # Table headers
        headers = QWidget()
        headers.setStyleSheet("""
            background-color: rgba(255,255,255,0.05);
            border-radius: 10px 10px 0 0;
        """)
        headers_layout = QHBoxLayout(headers)
        headers_layout.setContentsMargins(15, 15, 15, 15)
        headers_layout.setSpacing(15)
        
        for col, width in [("SIRA", 50), ("DURUM", 120), ("NOT", 200), ("SAAT", 70), ("İŞLEMLER", 150)]:
            lbl = QLabel(col)
            lbl.setStyleSheet("color: #9ca3af; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
            lbl.setMinimumWidth(width)
            headers_layout.addWidget(lbl)
        
        table_layout.addWidget(headers)
        
        # Scroll area for appointments
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(255,255,255,0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255,255,255,0.2);
                border-radius: 4px;
            }
        """)
        
        self.appointments_container = QWidget()
        self.appointments_layout = QVBoxLayout(self.appointments_container)
        self.appointments_layout.setContentsMargins(10, 10, 10, 10)
        self.appointments_layout.setSpacing(8)
        self.appointments_layout.addStretch()
        
        scroll.setWidget(self.appointments_container)
        table_layout.addWidget(scroll)
        
        layout.addWidget(table_container, stretch=1)
        
        # Footer
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_lbl = QLabel("🟢 Sistem Aktif")
        self.status_lbl.setStyleSheet("color: #6b7280; font-size: 12px;")
        footer_layout.addWidget(self.status_lbl)
        
        footer_layout.addStretch()
        
        last_update = QLabel(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        last_update.setStyleSheet("color: #6b7280; font-size: 11px;")
        footer_layout.addWidget(last_update)
        self.last_update_lbl = last_update
        
        layout.addWidget(footer)
        
        return content
    
    def apply_styles(self):
        self.setStyleSheet(ADMIN_STYLES)
    
    def _set_filter(self, filter_type):
        self.current_filter = filter_type
        self.sound.play_select()
        
        # Update nav active states
        for btn in [self.nav_all, self.nav_pending, self.nav_accepted, self.nav_rejected]:
            btn.setProperty("class", "nav-btn")
        
        if filter_type == "all":
            self.nav_all.setProperty("class", "nav-btn active")
            self.filter_lbl.setText("Tümü")
        elif filter_type == "pending":
            self.nav_pending.setProperty("class", "nav-btn active")
            self.filter_lbl.setText("Bekleyenler")
        elif filter_type == "accepted":
            self.nav_accepted.setProperty("class", "nav-btn active")
            self.filter_lbl.setText("Kabul Edilenler")
        elif filter_type == "rejected":
            self.nav_rejected.setProperty("class", "nav-btn active")
            self.filter_lbl.setText("Reddedilenler")
        
        # Refresh stylesheet
        for btn in [self.nav_all, self.nav_pending, self.nav_accepted, self.nav_rejected]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        self._load_data()
    
    def _toggle_sort(self):
        """Toggle between newest first and oldest first sorting"""
        self.sort_descending = not self.sort_descending
        if self.sort_descending:
            self.sort_btn.setText("↓ Yeniden Eskiye")
        else:
            self.sort_btn.setText("↑ Eskiden Yeniye")
        self.sound.play_select()
        self._load_data()
    
    def _auto_refresh(self):
        """Auto refresh with ringtone for new appointments"""
        try:
            stats = self.db.get_statistics()
            current_total = stats["total"]
            current_pending = stats["pending"]
            
            # Check for NEW appointments (total increased)
            if current_total > self.last_total and self.last_total > 0:
                new_count = current_total - self.last_total
                self.sound.play_ringtone()  # 🔔 RINGTONE for new appointments!
                self._show_new_appointment_notification(new_count)
            
            # Check for new pending appointments
            elif current_pending > self.last_pending and self.last_pending > 0:
                self.sound.play_ringtone()  # 🔔 RINGTONE for new pending!
            
            self.last_total = current_total
            self.last_pending = current_pending
            
            self._load_data(silent=True)
            
        except Exception as e:
            self.status_lbl.setText(f"🔴 Hata: {str(e)[:50]}")
    
    def _show_new_appointment_notification(self, count: int):
        """Show notification popup for new appointments"""
        msg = QMessageBox(self)
        msg.setWindowTitle("🔔 Yeni Randevu!")
        msg.setText(f"<b>{count} yeni randevu alındı!</b>")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: white;
                font-size: 16px;
                padding: 20px;
            }
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
        """)
        msg.exec()
    
    def _load_data(self, silent=False):
        """Load appointments and stats"""
        try:
            # Update stats
            stats = self.db.get_statistics()
            self.stat_total.set_value(stats["total"])
            self.stat_pending.set_value(stats["pending"])
            self.stat_accepted.set_value(stats["accepted"])
            self.stat_rejected.set_value(stats["rejected"])
            
            # Get appointments with sort order
            status_filter = None
            if self.current_filter == "pending":
                status_filter = AppointmentStatus.PENDING
            elif self.current_filter == "accepted":
                status_filter = AppointmentStatus.ACCEPTED
            elif self.current_filter == "rejected":
                status_filter = AppointmentStatus.REJECTED
            
            appointments = self.db.get_all_appointments(status_filter, descending=self.sort_descending)
            
            self._update_appointments_list(appointments)
            
            # Update status
            if not silent:
                self.status_lbl.setText("✅ Veriler güncellendi")
            self.last_update_lbl.setText(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_lbl.setText(f"🔴 Hata: {str(e)[:50]}")
    
    def _update_appointments_list(self, appointments: list):
        """Update the appointments list widget"""
        # Clear existing rows (except stretch)
        while self.appointments_layout.count() > 1:
            item = self.appointments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new rows
        for appt in appointments:
            row = AppointmentRow(appt)
            row.view_clicked.connect(self._on_view)
            row.accept_clicked.connect(self._on_accept)
            row.reject_clicked.connect(self._on_reject)
            row.delete_clicked.connect(self._on_delete)
            self.appointments_layout.insertWidget(self.appointments_layout.count() - 1, row)
    
    def _on_view(self, appt: Appointment):
        self.sound.play_select()
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Randevu #{appt.queue_number}")
        dlg.setMinimumSize(400, 300)
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(QLabel(f"<b>Sıra:</b> #{appt.queue_number}"))
        layout.addWidget(QLabel(f"<b>Durum:</b> {appt.status.value}"))
        layout.addWidget(QLabel(f"<b>Not:</b> {appt.note or '—'}"))
        layout.addWidget(QLabel(f"<b>Oluşturulma:</b> {appt.created_at.strftime('%d.%m.%Y %H:%M')}"))
        
        btn = AnimatedButton("Kapat", "#374151")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        
        dlg.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)
        dlg.exec()
    
    def _on_accept(self, id: int):
        if self.db.update_appointment_status(id, AppointmentStatus.ACCEPTED):
            self.sound.play_celebration()
            self._load_data()
    
    def _on_reject(self, id: int):
        if self.db.update_appointment_status(id, AppointmentStatus.REJECTED):
            self.sound.play_caution()
            self._load_data()
    
    def _on_delete(self, id: int):
        reply = QMessageBox.question(self, "Sil?", "Bu randevuyu silmek istediğinize emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_appointment(id):
                self.sound.play_notification()
                self._load_data()
    
    def closeEvent(self, e):
        self.timer.stop()
        e.accept()


def main():
    app = QApplication(sys.argv)
    
    # Modern font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1a1a2e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    app.setPalette(palette)
    
    window = AdminClient()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
