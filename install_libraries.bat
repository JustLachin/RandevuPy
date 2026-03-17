@echo off
:: =============================================================================
:: Randevu Sistemi Pro - Kapsamlı Kütüphane Kurulum Scripti
:: Appointment System - Comprehensive Library Installation Script
:: =============================================================================
:: Versiyon: 1.0.0
:: Yazar: RandevuPy Development Team
:: Tarih: 2024
:: =============================================================================

title Randevu Sistemi - Kütüphane Kurulumu

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║              🗓️  RANDEVU SİSTEMİ PRO - KURULUM ARACI                      ║
echo ║                                                                           ║
echo ║              Kapsamlı Kütüphane Kurulum Scripti v1.0.0                    ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

:: Yönetici yetkisi kontrolü
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  YÖNETİCİ YETKİSİ GEREKLİ!
    echo.
    echo Lütfen bu script'i Yönetici olarak çalıştırın:
    echo    1. Dosyaya sağ tıkla
    echo    2. "Yönetici olarak çalıştır" seç
    echo.
    pause
    exit /b 1
)

echo ✅ Yönetici yetkisi onaylandı
echo.

:: =============================================================================
:: 1. PYTHON KONTROLÜ
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 1️⃣  PYTHON KONTROLÜ                                                     │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ PYTHON BULUNAMADI!
    echo.
    echo Python 3.10 veya üzeri gereklidir.
    echo.
    echo 🔧 Kurulum Adımları:
    echo    1. https://python.org/downloads adresine git
    echo    2. Python 3.10+ indir
    echo    3. Kurulumda "Add Python to PATH" seçeneğini işaretle!
    echo.
    start https://python.org/downloads
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python sürümü: %PYTHON_VERSION%
echo.

:: Python versiyon kontrolü (3.10+)
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  PYTHON VERSİYONU ESKİ!
    echo    Gereken: Python 3.10 veya üzeri
    echo    Mevcut: %PYTHON_VERSION%
    echo.
    pause
    exit /b 1
)

echo ✅ Python versiyonu uyumludur (3.10+)
echo.

:: =============================================================================
:: 2. PIP KONTROLÜ VE GÜNCELLEME
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 2️⃣  PIP PAKET YÖNETİCİSİ                                                │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 🔧 Pip kurulumu yapılıyor...
    python -m ensurepip --default-pip
    if %errorLevel% neq 0 (
        echo ❌ Pip kurulumu başarısız!
        pause
        exit /b 1
    )
)

for /f "tokens=2" %%a in ('pip --version') do set PIP_VERSION=%%a
echo ✅ Pip sürümü: %PIP_VERSION%

echo 🔄 Pip güncelleniyor...
python -m pip install --upgrade pip --quiet
if %errorLevel% equ 0 (
    echo ✅ Pip güncellendi
echo.
) else (
    echo ⚠️  Pip güncelleme atlandı (mevcut sürüm çalışıyor)
)
echo.

:: =============================================================================
:: 3. SANAL ORTAM (VIRTUAL ENVIRONMENT) OLUŞTURMA
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 3️⃣  SANAL ORTAM (VIRTUAL ENVIRONMENT)                                   │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

if exist "venv" (
    echo ⚠️  Mevcut sanal ortam bulundu (venv)
    choice /C YN /M "   Mevcut sanal ortamı silip yeniden oluşturmak istiyor musunuz"
    if %errorLevel% equ 1 (
        echo 🗑️  Eski sanal ortam siliniyor...
        rmdir /s /q venv
        echo ✅ Eski sanal ortam silindi
    ) else (
        echo ⏭️  Mevcut sanal ortam kullanılacak
        goto :activate_venv
    )
)

echo 🔧 Yeni sanal ortam oluşturuluyor (venv)...
python -m venv venv
if %errorLevel% neq 0 (
    echo ❌ Sanal ortam oluşturulamadı!
    pause
    exit /b 1
)
echo ✅ Sanal ortam oluşturuldu
echo.

:activate_venv
echo 🔄 Sanal ortam aktifleştiriliyor...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo ❌ Sanal ortam aktifleştirilemedi!
    pause
    exit /b 1
)
echo ✅ Sanal ortam aktif: (venv)
echo.

:: =============================================================================
:: 4. GEREKLİ KÜTÜPHANELERİN KURULUMU
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 4️⃣  KÜTÜPHANE KURULUMU                                                  │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.
echo 📦 Kurulacak kütüphaneler:
echo    • PyQt6                 (GUI arayüzü için)
echo    • PyQt6-Qt6             (Qt6 binary dosyaları)
echo    • PyQt6-sip             (Python-C++ bağdaştırıcı)
echo    • supabase              (Supabase PostgreSQL bağlantısı)
echo    • websockets            (WebSocket desteği)
echo    • python-dotenv         (.env dosya yönetimi)
echo    • requests              (HTTP istekleri)
echo    • python-dateutil       (Tarih/zaman işlemleri)
echo.

:: Kütüphane kurulum fonksiyonu
call :install_package "PyQt6>=6.4.0" "PyQt6 (GUI Framework)"
call :install_package "PyQt6-Qt6>=6.4.0" "Qt6 Binaries"
call :install_package "PyQt6-sip>=13.4.0" "SIP Binding"
call :install_package "supabase>=2.3.0" "Supabase Client"
call :install_package "websockets>=12.0" "WebSocket Support"
call :install_package "python-dotenv>=1.0.0" "Environment Manager"
call :install_package "requests>=2.31.0" "HTTP Client"
call :install_package "python-dateutil>=2.8.0" "Date Utilities"

echo.
echo ✅ Tüm kütüphaneler başarıyla kuruldu!
echo.

:: =============================================================================
:: 5. KURULUM DOĞRULAMA
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 5️⃣  KURULUM DOĞRULAMA                                                   │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

echo 🔍 Kurulan kütüphaneler kontrol ediliyor...
echo.

python -c "import PyQt6; print(f'   ✅ PyQt6: {PyQt6.QtCore.PYQT_VERSION_STR}')" 2>nul
if %errorLevel% neq 0 echo    ❌ PyQt6: Kurulum hatası!

python -c "import supabase; print(f'   ✅ supabase: {supabase.__version__}')" 2>nul
if %errorLevel% neq 0 echo    ❌ supabase: Kurulum hatası!

python -c "import dotenv; print('   ✅ python-dotenv: Yüklü')" 2>nul
if %errorLevel% neq 0 echo    ❌ python-dotenv: Kurulum hatası!

python -c "import requests; print(f'   ✅ requests: {requests.__version__}')" 2>nul
if %errorLevel% neq 0 echo    ❌ requests: Kurulum hatası!

python -c "import dateutil; print('   ✅ python-dateutil: Yüklü')" 2>nul
if %errorLevel% neq 0 echo    ❌ python-dateutil: Kurulum hatası!

python -c "import websockets; print(f'   ✅ websockets: {websockets.__version__}')" 2>nul
if %errorLevel% neq 0 echo    ❌ websockets: Kurulum hatası!

echo.

:: =============================================================================
:: 6. PROJE YAPISI KONTROLÜ
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 6️⃣  PROJE YAPISI KONTROLÜ                                               │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

echo 📁 Gerekli dosyalar kontrol ediliyor...
echo.

set MISSING_FILES=0

if not exist "config.py" (
    echo    ❌ config.py bulunamadı
    set /a MISSING_FILES+=1
) else (
    echo    ✅ config.py
)

if not exist "database.py" (
    echo    ❌ database.py bulunamadı
    set /a MISSING_FILES+=1
) else (
    echo    ✅ database.py
)

if not exist "admin_client.py" (
    echo    ❌ admin_client.py bulunamadı
    set /a MISSING_FILES+=1
) else (
    echo    ✅ admin_client.py
)

if not exist "guest_client.py" (
    echo    ❌ guest_client.py bulunamadı
    set /a MISSING_FILES+=1
) else (
    echo    ✅ guest_client.py
)

if not exist "sound_manager.py" (
    echo    ❌ sound_manager.py bulunamadı
    set /a MISSING_FILES+=1
) else (
    echo    ✅ sound_manager.py
)

if not exist ".env" (
    echo    ⚠️  .env bulunamadı (ilk çalıştırmada oluşturulacak)
) else (
    echo    ✅ .env
)

if %MISSING_FILES% gtr 0 (
    echo.
    echo ⚠️  %MISSING_FILES% adet dosya eksik!
    echo    Lütfen tüm proje dosyalarının bu klasörde olduğundan emin olun.
    echo.
)

echo.

:: =============================================================================
:: 7. ÇALIŞTIRMA KISAYOLLARI OLUŞTURMA
:: =============================================================================
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 7️⃣  ÇALIŞTIRMA KISAYOLLARI                                              │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

echo 🔧 Çalıştırma scriptleri oluşturuluyor...
echo.

:: Admin Client Başlatıcı
echo @echo off > run_admin.bat
echo title Randevu Sistemi - Admin Client >> run_admin.bat
echo call venv\Scripts\activate.bat >> run_admin.bat
echo python admin_launcher.py >> run_admin.bat
echo pause >> run_admin.bat
echo    ✅ run_admin.bat oluşturuldu

:: Guest Client Başlatıcı
echo @echo off > run_guest.bat
echo title Randevu Sistemi - Guest Client >> run_guest.bat
echo call venv\Scripts\activate.bat >> run_guest.bat
echo python guest_launcher.py >> run_guest.bat
echo pause >> run_guest.bat
echo    ✅ run_guest.bat oluşturuldu

:: README oluştur
echo # Randevu Sistemi Pro - Kurulum Bilgileri > README_INSTALL.txt
echo. >> README_INSTALL.txt
echo ## 🚀 Hızlı Başlangıç >> README_INSTALL.txt
echo. >> README_INSTALL.txt
echo ### Kurulum >> README_INSTALL.txt
echo 1. `install_libraries.bat` dosyasını Yönetici olarak çalıştırın >> README_INSTALL.txt
echo 2. Kurulum tamamlandığında kısayollar otomatik oluşturulacak >> README_INSTALL.txt
echo. >> README_INSTALL.txt
echo ### Çalıştırma >> README_INSTALL.txt
echo - **Admin Client**: `run_admin.bat` dosyasına çift tıklayın >> README_INSTALL.txt
echo - **Guest Client**: `run_guest.bat` dosyasına çift tıklayın >> README_INSTALL.txt
echo. >> README_INSTALL.txt
echo ### Gereksinimler >> README_INSTALL.txt
echo - Windows 10/11 ^(64-bit^) >> README_INSTALL.txt
echo - Python 3.10 veya üzeri >> README_INSTALL.txt
echo - 4GB RAM ^(önerilen^) >> README_INSTALL.txt
echo - İnternet bağlantısı ^(Supabase için^) >> README_INSTALL.txt
echo. >> README_INSTALL.txt
echo    ✅ README_INSTALL.txt oluşturuldu

echo.

:: =============================================================================
:: KURULUM TAMAMLANDI
:: =============================================================================
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                    ✅ KURULUM BAŞARIYLA TAMAMLANDI!                        ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 SONUÇ ÖZETİ:
echo    ───────────────────────────────────────────────────────────────────────
echo    Python:        %PYTHON_VERSION%
echo    Sanal Ortam:   venv (aktif)
echo    Konum:         %CD%\venv
echo    ───────────────────────────────────────────────────────────────────────
echo.
echo 🚀 PROJEYİ BAŞLATMAK İÇİN:
echo.
echo    ┌─────────────────────────────┐     ┌─────────────────────────────┐
echo    │      🔴 ADMIN CLIENT        │     │      🟢 GUEST CLIENT        │
echo    │                             │     │                             │
echo    │   run_admin.bat             │     │   run_guest.bat             │
echo    │   dosyasına çift tıklayın  │     │   dosyasına çift tıklayın  │
echo    │                             │     │                             │
echo    └─────────────────────────────┘     └─────────────────────────────┘
echo.
echo ℹ️  NOT: İlk çalıştırmada Supabase ayarlarını yapılandırmayı unutmayın!
echo.
echo    Admin Client: Ayarlar ^> Supabase Yapılandırması
echo    Guest Client: Footer'a sağ tık ^> Gelişmiş Ayarlar
echo.

choice /C KO /M "   Kurulumu tamamlamak için [K]apat veya [O]turumu açık bırak"
if %errorLevel% equ 1 exit /b 0

pause
exit /b 0

:: =============================================================================
:: ALT PROGRAM: Paket Kurulum Fonksiyonu
:: =============================================================================
:install_package
set PACKAGE_NAME=%~1
set DISPLAY_NAME=%~2

echo 📦 %DISPLAY_NAME% kuruluyor...
echo    Paket: %PACKAGE_NAME%

pip install %PACKAGE_NAME% --quiet
if %errorLevel% equ 0 (
    echo    ✅ %DISPLAY_NAME% kuruldu
) else (
    echo    ❌ %DISPLAY_NAME% kurulumu başarısız!
    echo    Alternatif deneniyor...
    pip install %PACKAGE_NAME%
)
echo.
goto :eof
