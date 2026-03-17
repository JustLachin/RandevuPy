# Randevu Sistemi Pro - Kurulum Bilgileri

## 🚀 Hızlı Başlangıç

### Kurulum
```bash
python install.py
```

## .EXE ÇIKTISI BUILD ALMAK
```bash
python win_build.py
```

### Çalıştırma Seçenekleri

**Windows Batch:**
- Admin: `run_admin.bat`
- Guest: `run_guest.bat`

**PowerShell:**
- Admin: `run_admin.ps1`
- Guest: `run_guest.ps1`

**Python:**
- Admin: `python run_admin.py`
- Guest: `python run_guest.py`

### Gereksinimler
- Python 3.10+
- 4GB RAM (önerilen)
- İnternet bağlantısı

### Yüklü Kütüphaneler
| Kütüphane | Versiyon | Açıklama |
|-----------|----------|----------|
| PyQt6 | >=6.4.0 | GUI Framework - Qt6 Python Bindings |
| PyQt6-Qt6 | >=6.4.0 | Qt6 Binary Files - Platform Native Widgets |
| PyQt6-sip | >=13.4.0 | SIP Binding Generator - C++ Integration |
| supabase | >=2.3.0 | Supabase PostgreSQL Client - Cloud Database |
| websockets | >=12.0 | WebSocket Protocol - Real-time Communication |
| python-dotenv | >=1.0.0 | Environment Manager - .env File Support |
| requests | >=2.31.0 | HTTP Library - API Communication |
| python-dateutil | >=2.8.0 | Date/Time Utilities - Parsing & Formatting |

### İlk Yapılandırma
- **Admin**: Ayarlar > Supabase Yapılandırması
- **Guest**: Footer sağ tık > Gelişmiş Ayarlar

© 2024 RandevuPy
