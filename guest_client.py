"""
Randevu Sistemi - Guest Client Pro
Professional Appointment Booking Interface
"""
import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit, QMessageBox, QStackedWidget,
    QGraphicsDropShadowEffect, QSizePolicy, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QSize, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon

from database import get_db
from sound_manager import get_sound_manager
from config import AppConfig

# ============================================================
# GUEST STYLES
# ============================================================
GUEST_STYLES = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #334155);
}

.card {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.card-glass {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05));
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.input-field {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 18px 20px;
    font-size: 15px;
}

.input-field:focus {
    border-color: #818cf8;
    background-color: rgba(255, 255, 255, 0.15);
}

.btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #8b5cf6);
    color: white;
    border: none;
    border-radius: 20px;
    padding: 20px 40px;
    font-size: 16px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #818cf8, stop:1 #a78bfa);
}

.btn-secondary {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
    padding: 15px 30px;
    font-size: 14px;
    font-weight: 600;
}

.btn-secondary:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

.title-gradient {
    color: transparent;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #818cf8, stop:0.5 #a78bfa, stop:1 #f472b6);
}
"""

# ============================================================
# ANIMATED WIDGETS
# ============================================================

class SettingsDialog(QDialog):
    """Hidden settings dialog for Supabase configuration"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔧 Gelişmiş Ayarlar")
        self.setMinimumSize(500, 400)
        self.sound = get_sound_manager()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Warning header
        warning = QLabel("⚠️ Dikkat: Bu ayarları değiştirmek<br>veri kaybına neden olabilir!")
        warning.setStyleSheet("color: #fbbf24; font-size: 14px; font-weight: 600;")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning)
        
        # Header
        header = QLabel("🔌 Supabase Yapılandırması")
        header.setStyleSheet("font-size: 22px; font-weight: 700; color: #818cf8;")
        layout.addWidget(header)
        
        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # URL
        url_lbl = QLabel("🔌 Supabase URL")
        url_lbl.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: 600;")
        card_layout.addWidget(url_lbl)
        
        self.url_input = QLineEdit(AppConfig.SUPABASE_URL)
        self.url_input.setPlaceholderText("https://your-project.supabase.co")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.08);
                color: white;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #818cf8;
            }
        """)
        card_layout.addWidget(self.url_input)
        
        # Key
        key_lbl = QLabel("🔑 Supabase Anon Key")
        key_lbl.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: 600;")
        card_layout.addWidget(key_lbl)
        
        self.key_input = QLineEdit(AppConfig.SUPABASE_KEY)
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("eyJhbGciOiJIUzI1NiIs...")
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.08);
                color: white;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #818cf8;
            }
        """)
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
            QPushButton:hover {
                background-color: rgba(255,255,255,0.15);
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
        
        test_btn = AnimatedButton("🔗 Bağlantı Testi", primary=False)
        test_btn.clicked.connect(self._test_connection)
        btn_layout.addWidget(test_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = AnimatedButton("İptal", primary=False)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = AnimatedButton("💾 Kaydet", primary=True)
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


class AnimatedButton(QPushButton):
    """Button with scale animation on hover"""
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.is_primary = primary
        self.sound = get_sound_manager()
        self._setup_style()
        
        self._scale_anim = QPropertyAnimation(self, b"geometry")
        self._scale_anim.setDuration(200)
        self._scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _setup_style(self):
        if self.is_primary:
            self.setStyleSheet(GUEST_STYLES + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #6366f1, stop:1 #8b5cf6);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 20px 40px;
                    font-size: 16px;
                    font-weight: 700;
                }
            """)
        else:
            self.setStyleSheet(GUEST_STYLES + """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 16px;
                    padding: 15px 30px;
                    font-size: 14px;
                    font-weight: 600;
                }
            """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        self.sound.play_button()
        super().enterEvent(event)
    
    def mousePressEvent(self, event):
        self.sound.play_tap()
        super().mousePressEvent(event)


class SuccessCard(QFrame):
    """Animated success card showing appointment details"""
    def __init__(self, queue_number, note, parent=None):
        super().__init__(parent)
        self.queue_number = queue_number
        self.note = note
        self.setup_ui()
        
        # Animation
        self.setGraphicsEffect(QGraphicsDropShadowEffect(self, blurRadius=30, color=QColor("#6366f1")))
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(16, 185, 129, 0.3), stop:1 rgba(52, 211, 153, 0.1));
                border-radius: 30px;
                border: 2px solid rgba(52, 211, 153, 0.5);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Success icon
        icon = QLabel("🎉")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        
        # Title
        title = QLabel("Randevu Alındı!")
        title.setStyleSheet("""
            color: #34d399;
            font-size: 28px;
            font-weight: 800;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Queue number card
        number_card = QFrame()
        number_card.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
        """)
        number_layout = QVBoxLayout(number_card)
        number_layout.setContentsMargins(30, 20, 30, 20)
        
        number_lbl = QLabel(f"#{self.queue_number}")
        number_lbl.setStyleSheet("""
            color: white;
            font-size: 56px;
            font-weight: 900;
        """)
        number_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_layout.addWidget(number_lbl)
        
        sub_lbl = QLabel("Sıra Numaranız")
        sub_lbl.setStyleSheet("color: #9ca3af; font-size: 14px;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_layout.addWidget(sub_lbl)
        
        layout.addWidget(number_card)
        
        # Note
        if self.note:
            note_lbl = QLabel(f"📝 Not: {self.note}")
            note_lbl.setStyleSheet("color: #d1d5db; font-size: 14px;")
            note_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            note_lbl.setWordWrap(True)
            layout.addWidget(note_lbl)
        
        # Info
        info = QLabel("ℹ️ Lütfen sıra numaranızı not edin.<br>Admin onayı bekleniyor.")
        info.setStyleSheet("color: #6b7280; font-size: 13px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)


class GuestClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = get_db()
        self.sound = get_sound_manager()
        self.setWindowTitle(f"{AppConfig.APP_NAME} - Randevu Al")
        self.setMinimumSize(600, 800)
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)
        
        # Stacked widget for pages
        self.stack = QStackedWidget()
        
        # Page 1: Form
        form_page = self._create_form_page()
        self.stack.addWidget(form_page)
        
        # Page 2: Success
        self.success_page = QWidget()
        self.stack.addWidget(self.success_page)
        
        main_layout.addWidget(self.stack)
    
    def _create_form_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Header card
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(99, 102, 241, 0.3), stop:1 rgba(139, 92, 246, 0.1));
                border-radius: 30px;
                border: 1px solid rgba(139, 92, 246, 0.4);
            }
        """)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(50, 50, 50, 50)
        header_layout.setSpacing(15)
        
        # Icon
        icon = QLabel("📅")
        icon.setStyleSheet("font-size: 72px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon)
        
        # Title
        title = QLabel("Randevu Al")
        title.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: 800;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Hızlı ve kolay randevu oluşturun.<br>Sıra numaranız otomatik verilir.")
        subtitle.setStyleSheet("color: #9ca3af; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_card)
        
        # Form card
        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)
        
        # Note label
        note_lbl = QLabel("📝 Not (Opsiyonel)")
        note_lbl.setStyleSheet("color: #9ca3af; font-size: 14px; font-weight: 600;")
        form_layout.addWidget(note_lbl)
        
        # Note input - Fixed for proper typing
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Randevu ile ilgili özel bir notunuz varsa buraya yazabilirsiniz...")
        self.note_input.setAcceptRichText(False)
        self.note_input.setTabChangesFocus(False)
        self.note_input.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 16px;
                padding: 15px;
                font-size: 15px;
                font-family: 'Segoe UI', sans-serif;
                selection-background-color: #818cf8;
            }
            QTextEdit:focus {
                border-color: #818cf8;
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        self.note_input.setMinimumHeight(120)
        self.note_input.setMaximumHeight(180)
        self.note_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        form_layout.addWidget(self.note_input)
        
        # Submit button
        submit_btn = AnimatedButton("✨ RANDEVU OLUŞTUR", primary=True)
        submit_btn.setMinimumHeight(60)
        submit_btn.clicked.connect(self._create_appointment)
        form_layout.addWidget(submit_btn)
        
        layout.addWidget(form_card)
        
        # Info section
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(30, 30, 30, 30)
        info_layout.setSpacing(15)
        
        info_title = QLabel("ℹ️ Bilgilendirme")
        info_title.setStyleSheet("color: #818cf8; font-size: 16px; font-weight: 700;")
        info_layout.addWidget(info_title)
        
        for icon, text in [
            ("🎫", "Otomatik sıra numarası verilir"),
            ("⏳", "Admin onayı beklenir"),
            ("📱", "Sıra numaranızı kaydedin"),
        ]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px;")
            row_layout.addWidget(icon_lbl)
            
            text_lbl = QLabel(text)
            text_lbl.setStyleSheet("color: #9ca3af; font-size: 14px;")
            row_layout.addWidget(text_lbl)
            row_layout.addStretch()
            
            info_layout.addWidget(row)
        
        layout.addWidget(info_card)
        layout.addStretch()
        
        # Footer with hidden settings access
        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: Version (click 5 times for settings)
        self.version_lbl = QLabel(f"v{AppConfig.APP_VERSION}")
        self.version_lbl.setStyleSheet("color: #6b7280; font-size: 12px; cursor: pointer;")
        self.version_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.version_click_count = 0
        self.version_lbl.mousePressEvent = self._on_version_click
        footer_layout.addWidget(self.version_lbl)
        
        footer_layout.addStretch()
        
        # Right: Copyright with right-click menu
        self.footer = QLabel(f"© 2024 {AppConfig.APP_NAME}")
        self.footer.setStyleSheet("color: #6b7280; font-size: 12px;")
        self.footer.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.footer.customContextMenuRequested.connect(self._show_footer_menu)
        footer_layout.addWidget(self.footer)
        
        layout.addWidget(footer_widget)
        
        return page
    
    def _on_version_click(self, event):
        """Secret settings access - click 5 times on version"""
        self.version_click_count += 1
        if self.version_click_count >= 5:
            self.version_click_count = 0
            self._open_settings()
    
    def _show_footer_menu(self, position):
        """Right-click menu on footer"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e293b;
                color: white;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #6366f1;
            }
        """)
        
        about_action = menu.addAction("ℹ️ Hakkında")
        about_action.triggered.connect(self._show_about)
        
        settings_action = menu.addAction("🔧 Gelişmiş Ayarlar")
        settings_action.triggered.connect(self._open_settings)
        
        menu.exec(self.footer.mapToGlobal(position))
    
    def _show_about(self):
        """Show about dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("ℹ️ Hakkında")
        msg.setText(f"""
        <center>
        <h2>{AppConfig.APP_NAME}</h2>
        <p><b>Versiyon:</b> {AppConfig.APP_VERSION}</p>
        <p>Randevu sistemi misafir istemcisi</p>
        <p style='color:#6b7280;'>© 2024 Tüm Hakları Saklıdır</p>
        </center>
        """)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
        """)
        msg.exec()
    
    def _open_settings(self):
        """Open settings dialog"""
        dlg = SettingsDialog(self)
        dlg.exec()
    
    def _create_appointment(self):
        """Create appointment and show success"""
        note = self.note_input.toPlainText().strip()
        
        try:
            appointment = self.db.create_appointment(note)
            
            if appointment:
                self.sound.play_celebration()
                
                # Clear success page
                if self.success_page.layout():
                    # Remove old widgets
                    while self.success_page.layout().count():
                        item = self.success_page.layout().takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                else:
                    QVBoxLayout(self.success_page)
                
                # Add success card
                success_card = SuccessCard(appointment.queue_number, appointment.note)
                self.success_page.layout().addWidget(success_card, alignment=Qt.AlignmentFlag.AlignCenter)
                
                # Add new appointment button
                new_btn = AnimatedButton("➕ YENİ RANDEVU", primary=False)
                new_btn.clicked.connect(self._reset_form)
                self.success_page.layout().addWidget(new_btn, alignment=Qt.AlignmentFlag.AlignCenter)
                
                # Switch to success page
                self.stack.setCurrentIndex(1)
                
            else:
                self.sound.play_caution()
                QMessageBox.warning(self, "⚠️ Hata", "Randevu oluşturulamadı. Lütfen tekrar deneyin.")
                
        except Exception as e:
            self.sound.play_caution()
            QMessageBox.critical(self, "❌ Hata", f"Bir hata oluştu:\n{str(e)}")
    
    def _reset_form(self):
        """Reset form and go back to form page"""
        self.note_input.clear()
        self.stack.setCurrentIndex(0)
        self.sound.play_swipe()


def main():
    app = QApplication(sys.argv)
    
    # Modern font
    font = QFont("Segoe UI", 11)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#1e293b"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#334155"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#6366f1"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    app.setPalette(palette)
    
    window = GuestClient()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
