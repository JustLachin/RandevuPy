#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🗓️  RANDEVU SİSTEMİ PRO - KURULUM ARACI                    ║
║                                                                              ║
║                  RandevuPy - Kapsamlı Kütüphane Kurulum Scripti              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Versiyon: 1.0.0
Yazar: RandevuPy Development Team
Tarih: 2024

Bu script Python 3.10+ kontrolü, sanal ortam oluşturma, 
tüm gerekli kütüphanelerin kurulumu ve doğrulama işlemlerini yapar.

Kullanım:
    python install.py
    python install.py --verbose
    python install.py --skip-venv

Gereksinimler:
    - Python 3.10 veya üzeri
    - pip (Python paket yöneticisi)
    - İnternet bağlantısı
"""

import sys
import os
import subprocess
import argparse
import platform
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# KONFIGÜRASYON
# =============================================================================

SCRIPT_VERSION = "1.0.0"
MIN_PYTHON_VERSION = (3, 10)
VENV_NAME = "venv"

# Renk Kodları (Terminal için)
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Temel Renkler
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Arka Plan Renkleri
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

# Kütüphane Listesi
@dataclass
class Package:
    name: str
    version: str
    description: str
    import_name: str = ""
    version_attr: str = "__version__"
    required: bool = True
    
    def __post_init__(self):
        if not self.import_name:
            self.import_name = self.name.replace("-", "_")

PACKAGES = [
    Package(
        name="PyQt6",
        version=">=6.4.0",
        description="GUI Framework - Qt6 Python Bindings",
        import_name="PyQt6.QtCore",
        version_attr="PYQT_VERSION_STR"
    ),
    Package(
        name="PyQt6-Qt6",
        version=">=6.4.0",
        description="Qt6 Binary Files - Platform Native Widgets",
        required=True
    ),
    Package(
        name="PyQt6-sip",
        version=">=13.4.0",
        description="SIP Binding Generator - C++ Integration",
        required=True
    ),
    Package(
        name="supabase",
        version=">=2.3.0",
        description="Supabase PostgreSQL Client - Cloud Database",
        import_name="supabase"
    ),
    Package(
        name="websockets",
        version=">=12.0",
        description="WebSocket Protocol - Real-time Communication"
    ),
    Package(
        name="python-dotenv",
        version=">=1.0.0",
        description="Environment Manager - .env File Support",
        import_name="dotenv"
    ),
    Package(
        name="requests",
        version=">=2.31.0",
        description="HTTP Library - API Communication"
    ),
    Package(
        name="python-dateutil",
        version=">=2.8.0",
        description="Date/Time Utilities - Parsing & Formatting",
        import_name="dateutil"
    ),
]

# Proje Dosyaları
PROJECT_FILES = [
    ("config.py", "Yapılandırma Modülü"),
    ("database.py", "Veritabanı Yöneticisi"),
    ("admin_client.py", "Admin İstemcisi"),
    ("guest_client.py", "Guest İstemcisi"),
    ("sound_manager.py", "Ses Yöneticisi"),
    ("admin_launcher.py", "Admin Başlatıcı"),
    ("guest_launcher.py", "Guest Başlatıcı"),
]

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def clear_screen():
    """Terminal ekranını temizler"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_color(text: str, color: str = Colors.WHITE, bold: bool = False):
    """Renkli metin yazdırır"""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.RESET}")

def print_header():
    """Başlık yazdırır"""
    header = f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🗓️  RANDEVU SİSTEMİ PRO - KURULUM ARACI                    ║
║                                                                              ║
║                     Kapsamlı Kütüphane Kurulum Scripti v{SCRIPT_VERSION}                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(header)

def print_section(number: str, title: str):
    """Bölüm başlığı yazdırır"""
    print(f"""
{Colors.BLUE}┌──────────────────────────────────────────────────────────────────────────────┐
│ {number} {title:<74}│
└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}
""")

def print_success(message: str):
    """Başarı mesajı yazdırır"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Hata mesajı yazdırır"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Uyarı mesajı yazdırır"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    """Bilgi mesajı yazdırır"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

def run_command(command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Komut çalıştırır ve sonuç döndürür"""
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_python_version() -> Tuple[bool, str]:
    """Python versiyonunu kontrol eder"""
    current = sys.version_info
    required = MIN_PYTHON_VERSION
    
    if current >= required:
        version_str = f"{current.major}.{current.minor}.{current.micro}"
        return True, version_str
    else:
        return False, f"{current.major}.{current.minor}.{current.micro}"

def get_pip_version() -> str:
    """Pip versiyonunu döndürür"""
    try:
        import pip
        return pip.__version__
    except:
        code, stdout, _ = run_command([sys.executable, "-m", "pip", "--version"])
        if code == 0:
            parts = stdout.split()
            return parts[1] if len(parts) > 1 else "bilinmiyor"
        return "bilinmiyor"

# =============================================================================
# KURULUM SINIFI
# =============================================================================

class Installer:
    """Kapsamlı kurulum yöneticisi"""
    
    def __init__(self, verbose: bool = False, skip_venv: bool = False):
        self.verbose = verbose
        self.skip_venv = skip_venv
        self.venv_path = Path(VENV_NAME)
        self.python_executable = sys.executable
        self.pip_executable = [sys.executable, "-m", "pip"]
        
    def log(self, message: str, level: str = "info"):
        """Log mesajı yazar"""
        if level == "info":
            print_info(message)
        elif level == "success":
            print_success(message)
        elif level == "warning":
            print_warning(message)
        elif level == "error":
            print_error(message)
    
    def step_1_check_python(self) -> bool:
        """Python versiyon kontrolü"""
        print_section("1️⃣", "PYTHON VERSİYON KONTROLÜ")
        
        is_valid, version = check_python_version()
        
        if not is_valid:
            print_error(f"PYTHON VERSİYONU ESKİ! Gereken: {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+")
            print(f"\n{Colors.RED}Mevcut versiyon: {version}{Colors.RESET}")
            print(f"\n{Colors.YELLOW}🔧 Kurulum Adımları:{Colors.RESET}")
            print(f"   1. https://python.org/downloads adresine git")
            print(f"   2. Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ indir")
            print(f"   3. Kurulumda 'Add Python to PATH' seçeneğini işaretle!")
            return False
        
        print_success(f"Python versiyonu uyumlu: {version}")
        return True
    
    def step_2_upgrade_pip(self) -> bool:
        """Pip güncelleme"""
        print_section("2️⃣", "PIP GÜNCELLEME")
        
        current_version = get_pip_version()
        print_info(f"Mevcut pip versiyonu: {current_version}")
        
        print(f"\n{Colors.YELLOW}🔄 Pip güncelleniyor...{Colors.RESET}")
        code, stdout, stderr = run_command(
            self.pip_executable + ["install", "--upgrade", "pip", "-q"]
        )
        
        if code == 0:
            new_version = get_pip_version()
            print_success(f"Pip güncellendi: v{new_version}")
            return True
        else:
            print_warning("Pip güncelleme atlandı (mevcut sürüm çalışıyor)")
            return True
    
    def step_3_create_venv(self) -> bool:
        """Sanal ortam oluşturma"""
        if self.skip_venv:
            print_section("3️⃣", "SANAL ORTAM (ATLANDI)")
            print_info("Sanal ortam oluşturma atlandı (--skip-venv)")
            return True
        
        print_section("3️⃣", "SANAL ORTAM OLUŞTURMA")
        
        if self.venv_path.exists():
            print_warning(f"Mevcut sanal ortam bulundu: {VENV_NAME}")
            response = input(f"\n   {Colors.YELLOW}Mevcut ortamı silip yeniden oluşturmak istiyor musunuz? (E/H): {Colors.RESET}").strip().lower()
            
            if response == 'e':
                print_info("Eski sanal ortam siliniyor...")
                import shutil
                shutil.rmtree(self.venv_path)
                print_success("Eski sanal ortam silindi")
            else:
                print_info("Mevcut sanal ortam kullanılacak")
                return self._activate_venv()
        
        print(f"\n{Colors.YELLOW}🔧 Yeni sanal ortam oluşturuluyor ({VENV_NAME})...{Colors.RESET}")
        code, stdout, stderr = run_command([self.python_executable, "-m", "venv", VENV_NAME])
        
        if code != 0:
            print_error("Sanal ortam oluşturulamadı!")
            print(f"{Colors.RED}Hata: {stderr}{Colors.RESET}")
            return False
        
        print_success(f"Sanal ortam oluşturuldu: {VENV_NAME}")
        return self._activate_venv()
    
    def _activate_venv(self) -> bool:
        """Sanal ortamı aktifleştirir"""
        print(f"\n{Colors.YELLOW}🔄 Sanal ortam aktifleştiriliyor...{Colors.RESET}")
        
        if platform.system() == "Windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
            pip_path = self.venv_path / "Scripts" / "pip.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
            pip_path = self.venv_path / "bin" / "pip"
        
        if not python_path.exists():
            print_error("Sanal ortam Python executable bulunamadı!")
            return False
        
        self.python_executable = str(python_path)
        self.pip_executable = [str(python_path), "-m", "pip"]
        
        print_success(f"Sanal ortam aktif: ({VENV_NAME})")
        return True
    
    def step_4_install_packages(self) -> bool:
        """Kütüphaneleri kurar"""
        print_section("4️⃣", "KÜTÜPHANE KURULUMU")
        
        print(f"{Colors.CYAN}📦 Kurulacak kütüphaneler:{Colors.RESET}\n")
        for pkg in PACKAGES:
            print(f"   {Colors.DIM}•{Colors.RESET} {Colors.WHITE}{pkg.name}{Colors.RESET}{Colors.YELLOW}{pkg.version}{Colors.RESET}")
            print(f"     {Colors.DIM}{pkg.description}{Colors.RESET}")
        print()
        
        success_count = 0
        fail_count = 0
        
        for pkg in PACKAGES:
            print(f"{Colors.YELLOW}📦 {pkg.name} kuruluyor...{Colors.RESET}")
            if self.verbose:
                print(f"   {Colors.DIM}Paket: {pkg.name}{pkg.version}{Colors.RESET}")
            
            # Kurulum komutu
            code, stdout, stderr = run_command(
                self.pip_executable + ["install", f"{pkg.name}{pkg.version}", "-q"]
            )
            
            if code == 0:
                print_success(f"{pkg.name} kuruldu")
                success_count += 1
            else:
                print_error(f"{pkg.name} kurulumu başarısız!")
                if stderr and self.verbose:
                    print(f"   {Colors.RED}{stderr[:200]}{Colors.RESET}")
                fail_count += 1
                
                # Alternatif deneme
                if not pkg.required:
                    print_warning(f"   {pkg.name} opsiyonel, atlanıyor...")
                else:
                    print(f"{Colors.YELLOW}   Alternatif deneniyor...{Colors.RESET}")
                    code2, _, _ = run_command(
                        self.pip_executable + ["install", pkg.name]
                    )
                    if code2 == 0:
                        print_success(f"   {pkg.name} alternatif kurulumla başarılı")
                        success_count += 1
                        fail_count -= 1
        
        print(f"\n{Colors.CYAN}📊 Sonuç: {success_count} başarılı, {fail_count} başarısız{Colors.RESET}")
        return fail_count == 0 or success_count >= len([p for p in PACKAGES if p.required])
    
    def step_5_verify_packages(self) -> bool:
        """Kütüphaneleri doğrular"""
        print_section("5️⃣", "KURULUM DOĞRULAMA")
        
        print_info("Kurulan kütüphaneler kontrol ediliyor...\n")
        
        for pkg in PACKAGES:
            if not pkg.import_name:
                continue
                
            check_code = f"import {pkg.import_name}; print(getattr({pkg.import_name}, '{pkg.version_attr}', 'Yüklü'))"
            code, stdout, stderr = run_command([self.python_executable, "-c", check_code])
            
            if code == 0:
                version = stdout.strip()
                print_success(f"{pkg.name}: {version}")
            else:
                # Versiyonsuz kontrol
                check_code2 = f"import {pkg.import_name}"
                code2, _, _ = run_command([self.python_executable, "-c", check_code2])
                if code2 == 0:
                    print_success(f"{pkg.name}: Yüklü")
                else:
                    print_error(f"{pkg.name}: Kurulum hatası!")
        
        return True
    
    def step_6_check_project_files(self) -> bool:
        """Proje dosyalarını kontrol eder"""
        print_section("6️⃣", "PROJE YAPISI KONTROLÜ")
        
        print_info("Gerekli dosyalar kontrol ediliyor...\n")
        
        missing = 0
        for filename, description in PROJECT_FILES:
            filepath = Path(filename)
            if filepath.exists():
                print_success(f"{description}: {filename}")
            else:
                print_error(f"{description}: {filename} bulunamadı!")
                missing += 1
        
        env_file = Path(".env")
        if env_file.exists():
            print_success(f"Çevre değişkenleri: .env")
        else:
            print_warning(f"Çevre değişkenleri: .env (ilk çalıştırmada oluşturulacak)")
        
        if missing > 0:
            print(f"\n{Colors.YELLOW}⚠️  {missing} adet dosya eksik!{Colors.RESET}")
        
        return True
    
    def step_7_create_launchers(self) -> bool:
        """Çalıştırma dosyaları oluşturur"""
        print_section("7️⃣", "ÇALIŞTIRMA KISAYOLLARI")
        
        print_info("Çalıştırma scriptleri oluşturuluyor...\n")
        
        # Windows Batch Dosyaları
        admin_bat = f"""@echo off
title Randevu Sistemi - Admin Client
call {VENV_NAME}\\Scripts\\activate.bat
python admin_launcher.py
pause
"""
        
        guest_bat = f"""@echo off
title Randevu Sistemi - Guest Client
call {VENV_NAME}\\Scripts\\activate.bat
python guest_launcher.py
pause
"""
        
        # PowerShell Dosyaları
        admin_ps1 = f"""# Randevu Sistemi - Admin Client
& .\\{VENV_NAME}\\Scripts\\Activate.ps1
python admin_launcher.py
pause
"""
        
        guest_ps1 = f"""# Randevu Sistemi - Guest Client
& .\\{VENV_NAME}\\Scripts\\Activate.ps1
python guest_launcher.py
pause
"""
        
        # Python Launcher
        admin_py = f"""#!/usr/bin/env python3
import subprocess
import sys

subprocess.run([r"{VENV_NAME}\\Scripts\\python.exe", "admin_launcher.py"])
"""
        
        guest_py = f"""#!/usr/bin/env python3
import subprocess
import sys

subprocess.run([r"{VENV_NAME}\\Scripts\\python.exe", "guest_launcher.py"])
"""
        
        files_to_create = [
            ("run_admin.bat", admin_bat),
            ("run_guest.bat", guest_bat),
            ("run_admin.ps1", admin_ps1),
            ("run_guest.ps1", guest_ps1),
            ("run_admin.py", admin_py),
            ("run_guest.py", guest_py),
        ]
        
        for filename, content in files_to_create:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print_success(f"{filename} oluşturuldu")
            except Exception as e:
                print_error(f"{filename} oluşturulamadı: {e}")
        
        # README oluştur
        readme = f"""# Randevu Sistemi Pro - Kurulum Bilgileri

## 🚀 Hızlı Başlangıç

### Kurulum
```bash
python install.py
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
"""
        for pkg in PACKAGES:
            readme += f"| {pkg.name} | {pkg.version} | {pkg.description} |\n"
        
        readme += """
### İlk Yapılandırma
- **Admin**: Ayarlar > Supabase Yapılandırması
- **Guest**: Footer sağ tık > Gelişmiş Ayarlar

© 2024 RandevuPy
"""
        
        with open("README_INSTALL.txt", 'w', encoding='utf-8') as f:
            f.write(readme)
        print_success("README_INSTALL.txt oluşturuldu")
        
        return True
    
    def run(self) -> bool:
        """Tam kurulum sürecini çalıştırır"""
        clear_screen()
        print_header()
        
        steps = [
            ("Python Kontrolü", self.step_1_check_python),
            ("Pip Güncelleme", self.step_2_upgrade_pip),
            ("Sanal Ortam", self.step_3_create_venv),
            ("Kütüphane Kurulumu", self.step_4_install_packages),
            ("Doğrulama", self.step_5_verify_packages),
            ("Proje Kontrolü", self.step_6_check_project_files),
            ("Başlatıcılar", self.step_7_create_launchers),
        ]
        
        for i, (name, step_func) in enumerate(steps, 1):
            try:
                if not step_func():
                    print_error(f"'{name}' adımı başarısız!")
                    return False
            except Exception as e:
                print_error(f"'{name}' adımında hata: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                return False
        
        # Tamamlandı
        self._print_completion()
        return True
    
    def _print_completion(self):
        """Tamamlanma mesajını yazdırır"""
        print(f"""
{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ✅ KURULUM BAŞARIYLA TAMAMLANDI!                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.CYAN}📋 SONUÇ ÖZETİ:{Colors.RESET}
   {Colors.DIM}═══════════════════════════════════════════════════════════════════════{Colors.RESET}
   Python:        {Colors.WHITE}v{sys.version.split()[0]}{Colors.RESET}
   Sanal Ortam:   {Colors.WHITE}{VENV_NAME} (aktif){Colors.RESET}
   Konum:         {Colors.WHITE}{os.getcwd()}\\{VENV_NAME}{Colors.RESET}
   {Colors.DIM}═══════════════════════════════════════════════════════════════════════{Colors.RESET}

{Colors.YELLOW}🚀 PROJEYİ BAŞLATMAK İÇİN:{Colors.RESET}

   {Colors.BLUE}┌─────────────────────────────┐     ┌─────────────────────────────┐{Colors.RESET}
   {Colors.BLUE}│      🔴 ADMIN CLIENT        │     │      🟢 GUEST CLIENT        │{Colors.RESET}
   {Colors.BLUE}│                             │     │                             │{Colors.RESET}
   {Colors.GREEN}│   run_admin.bat             │     │   run_guest.bat             │{Colors.RESET}
   {Colors.GREEN}│   veya run_admin.py        │     │   veya run_guest.py        │{Colors.RESET}
   {Colors.BLUE}│                             │     │                             │{Colors.RESET}
   {Colors.BLUE}└─────────────────────────────┘     └─────────────────────────────┘{Colors.RESET}

{Colors.CYAN}ℹ️  NOT: İlk çalıştırmada Supabase ayarlarını yapılandırmayı unutmayın!{Colors.RESET}

   {Colors.WHITE}Admin Client: Ayarlar > Supabase Yapılandırması{Colors.RESET}
   {Colors.WHITE}Guest Client: Footer'a sağ tık > Gelişmiş Ayarlar{Colors.RESET}

{Colors.DIM}© 2024 RandevuPy - Tüm Hakları Saklıdır{Colors.RESET}
""")

# =============================================================================
# ANA PROGRAM
# =============================================================================

def main():
    """Ana program giriş noktası"""
    parser = argparse.ArgumentParser(
        description="Randevu Sistemi Pro - Kütüphane Kurulum Scripti",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek Kullanım:
  python install.py              # Normal kurulum
  python install.py --verbose    # Detaylı çıktı
  python install.py --skip-venv  # Sanal ortam olmadan kur
        """
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Detaylı çıktı modu"
    )
    
    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Sanal ortam oluşturmayı atla"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}"
    )
    
    args = parser.parse_args()
    
    # Windows için UTF-8 desteği
    if platform.system() == "Windows":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    installer = Installer(verbose=args.verbose, skip_venv=args.skip_venv)
    success = installer.run()
    
    if success:
        input(f"\n{Colors.YELLOW}   Devam etmek için ENTER'a basın...{Colors.RESET}")
        sys.exit(0)
    else:
        print_error("Kurulum başarısız oldu!")
        input(f"\n{Colors.YELLOW}   Çıkmak için ENTER'a basın...{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
