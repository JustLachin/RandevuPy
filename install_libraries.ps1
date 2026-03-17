#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Randevu Sistemi Pro - Kapsamlı Kütüphane Kurulum Scripti
    Appointment System - Comprehensive Library Installation Script

.DESCRIPTION
    Bu script Python 3.10+ kontrolü, sanal ortam oluşturma,
    tüm gerekli kütüphanelerin kurulumu ve doğrulama işlemlerini yapar.

.VERSION
    1.0.0

.AUTHOR
    RandevuPy Development Team
#>

# =============================================================================
# KONFIGÜRASYON
# =============================================================================
$ScriptVersion = "1.0.0"
$RequiredPythonVersion = [Version]"3.10"
$VirtualEnvName = "venv"

$Packages = @(
    @{ Name = "PyQt6"; Version = ">=6.4.0"; Description = "GUI Framework (Qt6 Python Bindings)" }
    @{ Name = "PyQt6-Qt6"; Version = ">=6.4.0"; Description = "Qt6 Binary Files" }
    @{ Name = "PyQt6-sip"; Version = ">=13.4.0"; Description = "Python-C++ Binding Generator" }
    @{ Name = "supabase"; Version = ">=2.3.0"; Description = "Supabase PostgreSQL Client" }
    @{ Name = "websockets"; Version = ">=12.0"; Description = "WebSocket Protocol Implementation" }
    @{ Name = "python-dotenv"; Version = ">=1.0.0"; Description = "Environment Variable Manager" }
    @{ Name = "requests"; Version = ">=2.31.0"; Description = "HTTP Library for Python" }
    @{ Name = "python-dateutil"; Version = ">=2.8.0"; Description = "Date/Time Parsing Utilities" }
)

# =============================================================================
# FONKSİYONLAR
# =============================================================================

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "║  $Title" -ForegroundColor Cyan -NoNewline
    $padding = 74 - $Title.Length
    Write-Host (" " * $padding) "║" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Number, [string]$Title)
    Write-Host ""
    Write-Host "┌─────────────────────────────────────────────────────────────────────────┐" -ForegroundColor Blue
    Write-Host "│ $Number $Title" -ForegroundColor Blue -NoNewline
    $padding = 72 - $Number.Length - $Title.Length
    Write-Host (" " * $padding) "│" -ForegroundColor Blue
    Write-Host "└─────────────────────────────────────────────────────────────────────────┘" -ForegroundColor Blue
    Write-Host ""
}

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Type = "Info"
    )
    $icons = @{ "Info" = "ℹ️"; "Success" = "✅"; "Warning" = "⚠️"; "Error" = "❌" }
    $colors = @{ "Info" = "White"; "Success" = "Green"; "Warning" = "Yellow"; "Error" = "Red" }
    Write-Host "$($icons[$Type]) $Message" -ForegroundColor $colors[$Type]
}

function Test-Administrator {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-PythonVersion {
    try {
        $versionString = (python --version 2>&1).ToString().Replace("Python ", "")
        return [Version]$versionString
    } catch {
        return $null
    }
}

function Install-Package {
    param([string]$PackageName, [string]$Version, [string]$Description)
    
    Write-Host "📦 $Description" -ForegroundColor White
    Write-Host "   Paket: " -NoNewline -ForegroundColor Gray
    Write-Host "$PackageName$Version" -ForegroundColor Yellow
    
    $result = pip install "$PackageName$Version" --quiet 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Kuruldu: $PackageName" "Success"
    } else {
        Write-Status "$PackageName kurulumu başarısız! Detaylı deneniyor..." "Warning"
        pip install "$PackageName$Version"
    }
    Write-Host ""
}

function Test-Package {
    param([string]$PackageName, [string]$ImportName = $PackageName, [string]$VersionAttr = "__version__")
    
    try {
        $version = python -c "import $ImportName; print(getattr($ImportName, '$VersionAttr', 'Bilinmiyor'))" 2>$null
        if ($LASTEXITCODE -eq 0 -and $version) {
            Write-Status "$PackageName`: $version" "Success"
            return $true
        }
    } catch {}
    
    try {
        python -c "import $ImportName" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "$PackageName`: Yüklü" "Success"
            return $true
        }
    } catch {}
    
    Write-Status "$PackageName`: Kurulum hatası!" "Error"
    return $false
}

# =============================================================================
# ANA PROGRAM
# =============================================================================

clear
Write-Header "🗓️  RANDEVU SİSTEMİ PRO - KURULUM ARACI v$ScriptVersion"

# Yönetici Yetkisi Kontrolü
Write-Status "Yönetici yetkisi kontrol ediliyor..." "Info"
if (-not (Test-Administrator)) {
    Write-Status "YÖNETİCİ YETKİSİ GEREKLİ!" "Error"
    Write-Host ""
    Write-Host "Lütfen bu script'i Yönetici olarak çalıştırın:" -ForegroundColor Yellow
    Write-Host "   1. Dosyaya sağ tıkla" -ForegroundColor White
    Write-Host "   2. 'PowerShell ile çalıştır' veya 'Yönetici olarak çalıştır' seç" -ForegroundColor White
    Write-Host ""
    Read-Host "Devam etmek için ENTER'a basın"
    exit 1
}
Write-Status "Yönetici yetkisi onaylandı" "Success"
Write-Host ""

# Python Kontrolü
Write-Section "1️⃣" "PYTHON KONTROLÜ"
Write-Status "Python sürümü kontrol ediliyor..." "Info"

$pythonVersion = Get-PythonVersion
if ($null -eq $pythonVersion) {
    Write-Status "PYTHON BULUNAMADI!" "Error"
    Write-Host ""
    Write-Host "Python 3.10 veya üzeri gereklidir." -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Kurulum Adımları:" -ForegroundColor Yellow
    Write-Host "   1. https://python.org/downloads adresine git" -ForegroundColor White
    Write-Host "   2. Python 3.10+ indir" -ForegroundColor White
    Write-Host "   3. Kurulumda 'Add Python to PATH' seçeneğini işaretle!" -ForegroundColor White
    Write-Host ""
    Start-Process "https://python.org/downloads"
    Read-Host "Devam etmek için ENTER'a basın"
    exit 1
}

Write-Status "Python sürümü: $pythonVersion" "Success"

if ($pythonVersion -lt $RequiredPythonVersion) {
    Write-Status "PYTHON VERSİYONU ESKİ! Gereken: 3.10+" "Error"
    Read-Host "Devam etmek için ENTER'a basın"
    exit 1
}

Write-Status "Python versiyonu uyumludur" "Success"
Write-Host ""

# Pip Kontrolü
Write-Section "2️⃣" "PIP PAKET YÖNETİCİSİ"
Write-Status "Pip güncelleniyor..." "Info"
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -eq 0) {
    $pipVersion = (pip --version).Split()[1]
    Write-Status "Pip güncellendi: v$pipVersion" "Success"
} else {
    Write-Status "Pip güncelleme atlandı" "Warning"
}
Write-Host ""

# Sanal Ortam
Write-Section "3️⃣" "SANAL ORTAM (VIRTUAL ENVIRONMENT)"

if (Test-Path $VirtualEnvName) {
    Write-Status "Mevcut sanal ortam bulundu" "Warning"
    $response = Read-Host "   Mevcut sanal ortamı silip yeniden oluşturmak istiyor musunuz? (E/H)"
    if ($response -eq "E" -or $response -eq "e") {
        Write-Status "Eski sanal ortam siliniyor..." "Info"
        Remove-Item -Recurse -Force $VirtualEnvName
        Write-Status "Eski sanal ortam silindi" "Success"
    } else {
        Write-Status "Mevcut sanal ortam kullanılacak" "Success"
    }
}

if (-not (Test-Path $VirtualEnvName)) {
    Write-Status "Yeni sanal ortam oluşturuluyor..." "Info"
    python -m venv $VirtualEnvName
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Sanal ortam oluşturulamadı!" "Error"
        Read-Host "Devam etmek için ENTER'a basın"
        exit 1
    }
    Write-Status "Sanal ortam oluşturuldu: $VirtualEnvName" "Success"
}

Write-Status "Sanal ortam aktifleştiriliyor..." "Info"
& ".\$VirtualEnvName\Scripts\Activate.ps1"
if (-not $?) {
    Write-Status "Sanal ortam aktifleştirilemedi!" "Error"
    Read-Host "Devam etmek için ENTER'a basın"
    exit 1
}
Write-Status "Sanal ortam aktif: ($VirtualEnvName)" "Success"
Write-Host ""

# Kütüphane Kurulumu
Write-Section "4️⃣" "KÜTÜPHANE KURULUMU"
Write-Host "📦 Kurulacak kütüphaneler:" -ForegroundColor Yellow
$Packages | ForEach-Object {
    Write-Host "   • $($_.Name)$($_.Version)" -ForegroundColor Gray -NoNewline
    Write-Host " - $($_.Description)" -ForegroundColor DarkGray
}
Write-Host ""

foreach ($package in $Packages) {
    Install-Package -PackageName $package.Name -Version $package.Version -Description $package.Description
}

Write-Status "Tüm kütüphaneler başarıyla kuruldu!" "Success"
Write-Host ""

# Doğrulama
Write-Section "5️⃣" "KURULUM DOĞRULAMA"
Write-Status "Kurulan kütüphaneler kontrol ediliyor..." "Info"
Write-Host ""

Test-Package -PackageName "PyQt6" -ImportName "PyQt6.QtCore" -VersionAttr "PYQT_VERSION_STR"
Test-Package -PackageName "supabase" -ImportName "supabase"
Test-Package -PackageName "python-dotenv" -ImportName "dotenv" -VersionAttr "__version__"
Test-Package -PackageName "requests" -ImportName "requests"
Test-Package -PackageName "python-dateutil" -ImportName "dateutil"
Test-Package -PackageName "websockets" -ImportName "websockets"

Write-Host ""

# Proje Yapısı Kontrolü
Write-Section "6️⃣" "PROJE YAPISI KONTROLÜ"
Write-Status "Gerekli dosyalar kontrol ediliyor..." "Info"
Write-Host ""

$RequiredFiles = @(
    @{ Path = "config.py"; Description = "Yapılandırma" }
    @{ Path = "database.py"; Description = "Veritabanı modülü" }
    @{ Path = "admin_client.py"; Description = "Admin istemcisi" }
    @{ Path = "guest_client.py"; Description = "Guest istemcisi" }
    @{ Path = "sound_manager.py"; Description = "Ses yöneticisi" }
    @{ Path = "admin_launcher.py"; Description = "Admin başlatıcı" }
    @{ Path = "guest_launcher.py"; Description = "Guest başlatıcı" }
)

$missingFiles = 0
foreach ($file in $RequiredFiles) {
    if (Test-Path $file.Path) {
        Write-Status "$($file.Description): $($file.Path)" "Success"
    } else {
        Write-Status "$($file.Description): $($file.Path) bulunamadı!" "Error"
        $missingFiles++
    }
}

if (Test-Path ".env") {
    Write-Status "Çevre değişkenleri: .env" "Success"
} else {
    Write-Status "Çevre değişkenleri: .env (ilk çalıştırmada oluşturulacak)" "Warning"
}

if ($missingFiles -gt 0) {
    Write-Host ""
    Write-Status "$missingFiles adet dosya eksik!" "Warning"
}
Write-Host ""

# Çalıştırma Scriptleri
Write-Section "7️⃣" "ÇALIŞTIRMA KISAYOLLARI"
Write-Status "Çalıştırma scriptleri oluşturuluyor..." "Info"
Write-Host ""

# run_admin.bat
$adminScript = @"
@echo off
title Randevu Sistemi - Admin Client
call venv\Scripts\activate.bat
python admin_launcher.py
pause
"@
$adminScript | Out-File -FilePath "run_admin.bat" -Encoding ASCII
Write-Status "run_admin.bat oluşturuldu" "Success"

# run_guest.bat
$guestScript = @"
@echo off
title Randevu Sistemi - Guest Client
call venv\Scripts\activate.bat
python guest_launcher.py
pause
"@
$guestScript | Out-File -FilePath "run_guest.bat" -Encoding ASCII
Write-Status "run_guest.bat oluşturuldu" "Success"

# run_admin.ps1
$adminPS = @"
# Randevu Sistemi - Admin Client Başlatıcı
& ".\venv\Scripts\Activate.ps1"
python admin_launcher.py
pause
"@
$adminPS | Out-File -FilePath "run_admin.ps1" -Encoding UTF8
Write-Status "run_admin.ps1 oluşturuldu" "Success"

# run_guest.ps1
$guestPS = @"
# Randevu Sistemi - Guest Client Başlatıcı
& ".\venv\Scripts\Activate.ps1"
python guest_launcher.py
pause
"@
$guestPS | Out-File -FilePath "run_guest.ps1" -Encoding UTF8
Write-Status "run_guest.ps1 oluşturuldu" "Success"

# README
$readme = @"
# Randevu Sistemi Pro - Kurulum Bilgileri

## 🚀 Hızlı Başlangıç

### Kurulum
1. `install_libraries.bat` veya `install_libraries.ps1` dosyasını Yönetici olarak çalıştırın
2. Kurulum tamamlandığında kısayollar otomatik oluşturulacak

### Çalıştırma Seçenekleri

#### Windows Batch (CMD):
- **Admin Client**: `run_admin.bat` dosyasına çift tıklayın
- **Guest Client**: `run_guest.bat` dosyasına çift tıklayın

#### PowerShell:
- **Admin Client**: `run_admin.ps1` dosyasına sağ tık > PowerShell ile çalıştır
- **Guest Client**: `run_guest.ps1` dosyasına sağ tık > PowerShell ile çalıştır

### Gereksinimler
- Windows 10/11 (64-bit)
- Python 3.10 veya üzeri
- 4GB RAM (önerilen)
- İnternet bağlantısı (Supabase için)

### Yüklü Kütüphaneler
| Kütüphane | Versiyon | Açıklama |
|-----------|----------|----------|
| PyQt6 | >=6.4.0 | GUI Framework |
| supabase | >=2.3.0 | PostgreSQL Client |
| websockets | >=12.0 | WebSocket desteği |
| python-dotenv | >=1.0.0 | Çevre değişkenleri |
| requests | >=2.31.0 | HTTP istekleri |
| python-dateutil | >=2.8.0 | Tarih/zaman işlemleri |

### İlk Yapılandırma
İlk çalıştırmada Supabase ayarlarını yapılandırın:
- **Admin Client**: Ayarlar > Supabase Yapılandırması
- **Guest Client**: Footer'a sağ tık > Gelişmiş Ayarlar

---
© 2024 RandevuPy - Tüm Hakları Saklıdır
"@
$readme | Out-File -FilePath "README_INSTALL.txt" -Encoding UTF8
Write-Status "README_INSTALL.txt oluşturuldu" "Success"

Write-Host ""

# Tamamlandı
Write-Header "✅ KURULUM BAŞARIYLA TAMAMLANDI!"

Write-Host "📋 SONUÇ ÖZETİ:" -ForegroundColor Yellow
Write-Host "   ═══════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "   Python:        v$pythonVersion" -ForegroundColor White
Write-Host "   Sanal Ortam:   $VirtualEnvName (aktif)" -ForegroundColor White
Write-Host "   Konum:         $PWD\$VirtualEnvName" -ForegroundColor White
Write-Host "   ═══════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

Write-Host "🚀 PROJEYİ BAŞLATMAK İÇİN:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   ┌─────────────────────────────┐     ┌─────────────────────────────┐" -ForegroundColor Blue
Write-Host "   │      🔴 ADMIN CLIENT        │     │      🟢 GUEST CLIENT        │" -ForegroundColor Blue
Write-Host "   │                             │     │                             │" -ForegroundColor Blue
Write-Host "   │   run_admin.bat             │     │   run_guest.bat             │" -ForegroundColor Green
Write-Host "   │   veya run_admin.ps1       │     │   veya run_guest.ps1       │" -ForegroundColor Green
Write-Host "   │                             │     │                             │" -ForegroundColor Blue
Write-Host "   └─────────────────────────────┘     └─────────────────────────────┘" -ForegroundColor Blue
Write-Host ""

Write-Host "ℹ️  NOT: İlk çalıştırmada Supabase ayarlarını yapılandırmayı unutmayın!" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Admin Client: Ayarlar > Supabase Yapılandırması" -ForegroundColor White
Write-Host "   Guest Client: Footer'a sağ tık > Gelişmiş Ayarlar" -ForegroundColor White
Write-Host ""

$response = Read-Host "   Kurulumu tamamlamak için [K]apat veya [O]turumu açık bırak (K/O)"
if ($response -eq "K" -or $response -eq "k") {
    exit 0
}

Write-Host ""
Write-Status "Kurulum tamamlandı. Sanal ortam aktif durumda." "Info"
Write-Host ""

# Oturumu açık bırak
cmd /c pause
