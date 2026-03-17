#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🗓️  RANDEVU SİSTEMİ PRO - EXE BUILD ARACI                   ║
║                                                                              ║
║                    PyInstaller Windows EXE Oluşturma Scripti                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Versiyon: 1.0.0
Yazar: RandevuPy Development Team

ÖZELLİKLER:
    ✅ --onefolder (onedir) modu - Açık kaynak yapı
    ✅ Admin ve Guest ayrı ayrı build alma
    ✅ Ses dosyaları ve varlıkları otomatik kopyalama
    ✅ Farklı bilgisayarlarda dağıtım için hazır paketler
    ✅ Otomatik .env yapılandırma şablonu

Kullanım:
    python win_build.py
    python win_build.py --clean
    python win_build.py --skip-guest
    python win_build.py --skip-admin

Çıktılar:
    dist/RandevuAdmin/     -> Admin Client EXE
    dist/RandevuGuest/     -> Guest Client EXE
"""

import sys
import os
import shutil
import subprocess
import argparse
import platform
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

# =============================================================================
# KONFIGÜRASYON
# =============================================================================

SCRIPT_VERSION = "1.0.0"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Renk Kodları
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

# Build Ayarları
@dataclass
class BuildConfig:
    name: str
    launcher: str
    output_name: str
    dist_name: str
    icon: str = ""
    console: bool = True
    hidden_imports: List[str] = None
    data_files: List[Tuple[str, str]] = None
    
    def __post_init__(self):
        if self.hidden_imports is None:
            self.hidden_imports = []
        if self.data_files is None:
            self.data_files = []

# Admin Client Yapılandırması
ADMIN_CONFIG = BuildConfig(
    name="Admin Client",
    launcher="admin_launcher.py",
    output_name="RandevuAdmin",
    dist_name="RandevuAdmin",
    console=False,  # GUI uygulaması, konsol gösterme
    hidden_imports=[
        "PyQt6.sip",
        "supabase",
        "dotenv",
        "requests",
        "dateutil",
        "websockets",
    ],
    data_files=[]
)

# Guest Client Yapılandırması
GUEST_CONFIG = BuildConfig(
    name="Guest Client",
    launcher="guest_launcher.py",
    output_name="RandevuGuest",
    dist_name="RandevuGuest",
    console=False,  # GUI uygulaması
    hidden_imports=[
        "PyQt6.sip",
        "supabase",
        "dotenv",
        "requests",
        "dateutil",
        "websockets",
    ],
    data_files=[]
)

# Gerekli Dosyalar
REQUIRED_FILES = [
    "config.py",
    "database.py",
    "admin_client.py",
    "guest_client.py",
    "sound_manager.py",
    "admin_launcher.py",
    "guest_launcher.py",
]

# Ses Dosyaları Dizini
SOUNDS_DIR = "SND01-sine-sound-pack"

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def clear_screen():
    """Ekranı temizler"""
    os.system('cls' if platform.system() == "Windows" else 'clear')

def print_color(text: str, color: str = Colors.WHITE, bold: bool = False):
    """Renkli metin yazdırır"""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.RESET}")

def print_header():
    """Başlık yazdırır"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🗓️  RANDEVU SİSTEMİ PRO - EXE BUILD                        ║
║                                                                              ║
║                     PyInstaller Windows Build Script v{SCRIPT_VERSION}                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

def print_section(number: str, title: str):
    """Bölüm başlığı yazdırır"""
    print(f"""
{Colors.BLUE}┌──────────────────────────────────────────────────────────────────────────────┐
│ {number} {title:<74}│
└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}
""")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

def run_command(command: List[str], cwd: Optional[str] = None, capture: bool = True) -> Tuple[int, str, str]:
    """Komut çalıştırır"""
    try:
        if capture:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(command, cwd=cwd)
            return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)

def check_pyinstaller() -> bool:
    """PyInstaller'ın kurulu olup olmadığını kontrol eder"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller() -> bool:
    """PyInstaller'ı kurar"""
    print_info("PyInstaller kuruluyor...")
    code, _, stderr = run_command([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
    if code == 0:
        print_success("PyInstaller kuruldu")
        return True
    else:
        print_error(f"PyInstaller kurulumu başarısız: {stderr}")
        return False

def check_files() -> Tuple[bool, List[str]]:
    """Gerekli dosyaların varlığını kontrol eder"""
    missing = []
    for filename in REQUIRED_FILES:
        if not Path(filename).exists():
            missing.append(filename)
    return len(missing) == 0, missing

# =============================================================================
# BUILD FONKSİYONLARI
# =============================================================================

def clean_build_directories():
    """Eski build dizinlerini temizler"""
    print_section("🧹", "BUILD DİZİNLERİ TEMİZLENİYOR")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    cleaned = 0
    
    for dirname in dirs_to_clean:
        path = Path(dirname)
        if path.exists():
            try:
                shutil.rmtree(path)
                print_success(f"{dirname}/ temizlendi")
                cleaned += 1
            except Exception as e:
                print_warning(f"{dirname}/ temizlenemedi: {e}")
    
    # .pyc dosyalarını temizle
    for pyc_file in Path(".").rglob("*.pyc"):
        try:
            pyc_file.unlink()
        except:
            pass
    
    for pycache in Path(".").rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
        except:
            pass
    
    if cleaned == 0:
        print_info("Temizlenecek build dizini bulunamadı")
    
    return True

def copy_sounds_to_dist(dist_path: Path):
    """Ses dosyalarını dist dizinine kopyalar"""
    sounds_src = Path(SOUNDS_DIR)
    if not sounds_src.exists():
        print_warning(f"{SOUNDS_DIR}/ dizini bulunamadı, atlanıyor...")
        return True
    
    sounds_dst = dist_path / SOUNDS_DIR
    try:
        if sounds_dst.exists():
            shutil.rmtree(sounds_dst)
        shutil.copytree(sounds_src, sounds_dst)
        print_success(f"Ses dosyaları kopyalandı: {sounds_dst}")
        return True
    except Exception as e:
        print_error(f"Ses dosyaları kopyalanamadı: {e}")
        return False

def create_env_template(dist_path: Path):
    """.env şablonu oluşturur"""
    env_template = """# Randevu Sistemi Pro - Supabase Yapılandırması
# Bu dosyayı kendi Supabase bilgilerinizle güncelleyin

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Not: Bu bilgileri Supabase Dashboard > Settings > API bölümünden alabilirsiniz
"""
    env_path = dist_path / ".env.template"
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        print_success(f".env şablonu oluşturuldu: {env_path}")
        return True
    except Exception as e:
        print_error(f".env şablonu oluşturulamadı: {e}")
        return False

def create_readme(dist_path: Path, config: BuildConfig):
    """README dosyası oluşturur"""
    readme = f"""# {config.name} - Dağıtım Paketi

## 🚀 Hızlı Başlık

1. **EXE'yi çalıştırın:**
   - `{config.output_name}.exe` dosyasına çift tıklayın

2. **İlk Yapılandırma:**
   - `.env.template` dosyasını `.env` olarak kopyalayın
   - Kendi Supabase bilgilerinizi girin

## 📁 Dosya Yapısı

```
{config.dist_name}/
├── {config.output_name}.exe    # Ana uygulama
├── {SOUNDS_DIR}/               # Ses dosyaları
├── .env.template               # Yapılandırma şablonu
└── README.txt                  # Bu dosya
```

## ⚙️ Yapılandırma

`.env` dosyasını düzenleyin:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

## 🖥️ Sistem Gereksinimleri

- Windows 10/11 (64-bit)
- 4GB RAM (önerilen)
- İnternet bağlantısı

## 📝 Notlar

- Bu uygulama açık kaynak yapıda (onefolder) derlenmiştir
- Tüm bağımlılıklar `_internal` klasöründedir
- Antivirüs yazılımları bazen uyarı verebilir (güvenli dosyalar)

---
Build Tarihi: {BUILD_DATE}
RandevuPy v{SCRIPT_VERSION}
© 2024 Tüm Hakları Saklıdır
"""
    readme_path = dist_path / "README.txt"
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        print_success(f"README oluşturuldu: {readme_path}")
        return True
    except Exception as e:
        print_error(f"README oluşturulamadı: {e}")
        return False

def build_executable(config: BuildConfig, verbose: bool = False) -> bool:
    """PyInstaller ile EXE oluşturur"""
    print_section(f"🔨", f"{config.name} BUILD İŞLEMİ")
    
    print_info(f"Build başlıyor: {config.launcher}")
    print(f"   {Colors.DIM}Çıktı: {config.output_name}.exe{Colors.RESET}")
    print(f"   {Colors.DIM}Mod: --onedir (klasör yapısı){Colors.RESET}\n")
    
    # PyInstaller komutu oluştur
    cmd = [
        sys.executable, "-m", "PyInstaller",
        config.launcher,
        "--name", config.output_name,
        "--onedir",  # Klasör yapısı (--onefile DEĞİL!)
        "--clean",
        "--noconfirm",
    ]
    
    # Konsol gösterme (GUI uygulaması)
    if not config.console:
        cmd.append("--windowed")
        cmd.append("--noconsole")
    
    # Gizli importlar
    for imp in config.hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Veri dosyaları
    # Ses dosyalarını ekle
    if Path(SOUNDS_DIR).exists():
        cmd.extend(["--add-data", f"{SOUNDS_DIR}{os.pathsep}{SOUNDS_DIR}"])
    
    # .env varsa ekle
    if Path(".env").exists():
        cmd.extend(["--add-data", f".env{os.pathsep}."])
    
    # Build işlemi
    print(f"{Colors.YELLOW}🔄 PyInstaller çalışıyor...{Colors.RESET}\n")
    
    if verbose:
        code = subprocess.call(cmd)
        stdout, stderr = "", ""
    else:
        code, stdout, stderr = run_command(cmd, capture=True)
    
    if code != 0:
        print_error(f"Build başarısız! (Kod: {code})")
        if stderr and not verbose:
            print(f"{Colors.RED}{stderr[:500]}{Colors.RESET}")
        return False
    
    print_success(f"Build tamamlandı: {config.output_name}.exe")
    
    # Dist klasörüne ses dosyalarını kopyala (ekstra güvenlik)
    dist_path = Path("dist") / config.dist_name
    if dist_path.exists():
        copy_sounds_to_dist(dist_path)
        create_env_template(dist_path)
        create_readme(dist_path, config)
    
    return True

def create_distribution_package(config: BuildConfig) -> bool:
    """Dağıtım paketi oluşturur (ZIP)"""
    print_info(f"{config.name} dağıtım paketi oluşturuluyor...")
    
    dist_path = Path("dist") / config.dist_name
    if not dist_path.exists():
        print_error(f"Build çıktısı bulunamadı: {dist_path}")
        return False
    
    zip_path = Path("dist") / f"{config.dist_name}_v{SCRIPT_VERSION}.zip"
    
    try:
        # ZIP oluştur
        shutil.make_archive(
            str(zip_path).replace(".zip", ""),
            'zip',
            str(dist_path)
        )
        print_success(f"Dağıtım paketi oluşturuldu: {zip_path}")
        return True
    except Exception as e:
        print_error(f"Paket oluşturulamadı: {e}")
        return False

def create_deployment_guide():
    """Dağıtım kılavuzu oluşturur"""
    guide = f"""# 🚀 DAĞITIM KILAVUZU - Randevu Sistemi Pro

## 📦 Build Çıktıları

Build işlemi tamamlandı! Aşağıdaki paketler oluşturuldu:

### 1️⃣ Admin Client
**Konum:** `dist/RandevuAdmin/`
**Paket:** `dist/RandevuAdmin_v{SCRIPT_VERSION}.zip`

Bu paket **admin/resepsiyon bilgisayarına** kurulacak:
- Randevu yönetimi
- İstatistikler
- Kabul/Red işlemleri
- Sesli bildirimler

### 2️⃣ Guest Client
**Konum:** `dist/RandevuGuest/`
**Paket:** `dist/RandevuGuest_v{SCRIPT_VERSION}.zip`

Bu paket **misafir/müşteri bilgisayarına** kurulacak:
- Randevu oluşturma
- Sıra numarası alma
- Not ekleme

---

## 💻 Kurulum Adımları

### Admin Client Kurulumu (Admin PC)

1. **Paketi çıkar:**
   ```
   RandevuAdmin_v{SCRIPT_VERSION}.zip → C:/RandevuAdmin/
   ```

2. **Yapılandırma:**
   - `.env.template` dosyasını `.env` olarak kopyala
   - Supabase URL ve Key'i gir

3. **Çalıştır:**
   - `RandevuAdmin.exe` çift tıkla

### Guest Client Kurulumu (Misafir PC)

1. **Paketi çıkar:**
   ```
   RandevuGuest_v{SCRIPT_VERSION}.zip → C:/RandevuGuest/
   ```

2. **Yapılandırma:**
   - `.env.template` dosyasını `.env` olarak kopyala
   - **Aynı Supabase bilgilerini** gir (Admin ile aynı olmalı!)

3. **Çalıştır:**
   - `RandevuGuest.exe` çift tıkla

---

## 🔧 Yapılandırma Detayları

### .env Dosyası

Her iki client'te de aynı Supabase bilgileri olmalı:

```env
SUPABASE_URL=https://whfmxhuawhnlkkegkayn.supabase.co
SUPABASE_KEY=sb_publishable_sC8d3SO0mE33WTLFUyrwiQ_ZPNrB7Sh
```

### Supabase Ayarları

1. Supabase Dashboard'a git
2. Project Settings > API
3. URL ve anon/public key'i kopyala
4. Her iki .env dosyasına yapıştır

---

## 🌐 Ağ Gereksinimleri

- Her iki bilgisayarın internete erişimi olmalı
- Supabase cloud veritabanına erişim gerekiyor
- Yerel ağ (LAN) bağlantısı gerekli değil
- Farklı lokasyonlarda çalışabilir

---

## ⚠️ Önemli Notlar

1. **Aynı Supabase:** Her iki client aynı Supabase projesine bağlanmalı
2. **API Key:** `anon` public key kullanın (service role key değil!)
3. **RLS Policies:** Supabase'de Row Level Security aktif olmalı
4. **Firewall:** 443 portu (HTTPS) açık olmalı

---

## 🆘 Sorun Giderme

### EXE Açılmıyor
- Windows Defender/Antivirüs uyarısı verebilir
- "Daha fazla bilgi" > "Yine de çalıştır" seçin

### Bağlantı Hatası
- .env dosyasındaki URL ve Key kontrol et
- İnternet bağlantısını kontrol et
- Supabase projesinin aktif olduğundan emin ol

### Ses Çalmıyor
- `sounds/` klasörü EXE ile aynı konumda mı kontrol et
- Windows ses seviyesini kontrol et

---

Build Tarihi: {BUILD_DATE}
Versiyon: {SCRIPT_VERSION}
"""
    
    guide_path = Path("dist") / "DEPLOYMENT_GUIDE.txt"
    try:
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        print_success(f"Dağıtım kılavuzu oluşturuldu: {guide_path}")
        return True
    except Exception as e:
        print_error(f"Kılavuz oluşturulamadı: {e}")
        return False

# =============================================================================
# ANA PROGRAM
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Randevu Sistemi Pro - EXE Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek Kullanım:
  python win_build.py              # Her iki client'i de build al
  python win_build.py --clean      # Önce temizle, sonra build al
  python win_build.py --skip-guest # Sadece Admin build al
  python win_build.py --skip-admin # Sadece Guest build al
  python win_build.py --verbose    # Detaylı çıktı
        """
    )
    
    parser.add_argument("--clean", action="store_true", help="Önce build dizinlerini temizle")
    parser.add_argument("--skip-admin", action="store_true", help="Admin client build alma")
    parser.add_argument("--skip-guest", action="store_true", help="Guest client build alma")
    parser.add_argument("--verbose", action="store_true", help="Detaylı çıktı")
    parser.add_argument("--version", action="version", version=f"%(prog)s {SCRIPT_VERSION}")
    
    args = parser.parse_args()
    
    # Windows UTF-8 desteği
    if platform.system() == "Windows":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    clear_screen()
    print_header()
    
    # PyInstaller kontrolü
    print_section("1️⃣", "PYINSTALLER KONTROLÜ")
    if not check_pyinstaller():
        print_warning("PyInstaller bulunamadı!")
        if not install_pyinstaller():
            print_error("Kurulum başarısız! Manuel kurun: pip install pyinstaller")
            input(f"\n{Colors.YELLOW}Çıkmak için ENTER...{Colors.RESET}")
            sys.exit(1)
    else:
        print_success("PyInstaller yüklü")
    
    # Dosya kontrolü
    print_section("2️⃣", "PROJE DOSYALARI KONTROLÜ")
    files_ok, missing = check_files()
    if not files_ok:
        print_error(f"Eksik dosyalar: {', '.join(missing)}")
        input(f"\n{Colors.YELLOW}Çıkmak için ENTER...{Colors.RESET}")
        sys.exit(1)
    print_success("Tüm proje dosyaları mevcut")
    
    # Temizleme
    if args.clean:
        clean_build_directories()
    
    # Build işlemleri
    results = {"admin": False, "guest": False}
    
    # Admin Build
    if not args.skip_admin:
        results["admin"] = build_executable(ADMIN_CONFIG, args.verbose)
        if results["admin"]:
            create_distribution_package(ADMIN_CONFIG)
    else:
        print_info("Admin build atlandı (--skip-admin)")
    
    # Guest Build
    if not args.skip_guest:
        results["guest"] = build_executable(GUEST_CONFIG, args.verbose)
        if results["guest"]:
            create_distribution_package(GUEST_CONFIG)
    else:
        print_info("Guest build atlandı (--skip-guest)")
    
    # Dağıtım kılavuzu
    if results["admin"] or results["guest"]:
        print_section("📦", "DAĞITIM PAKETLERİ")
        create_deployment_guide()
    
    # Özet
    print(f"""
{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ✅ BUILD İŞLEMİ TAMAMLANDI!                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.CYAN}📂 Çıktı Konumları:{Colors.RESET}
""")
    
    if results["admin"]:
        print(f"   {Colors.GREEN}✅{Colors.RESET} {Colors.WHITE}Admin Client:{Colors.RESET}  dist/RandevuAdmin/RandevuAdmin.exe")
        print(f"      {Colors.DIM}Paket: dist/RandevuAdmin_v{SCRIPT_VERSION}.zip{Colors.RESET}")
    
    if results["guest"]:
        print(f"   {Colors.GREEN}✅{Colors.RESET} {Colors.WHITE}Guest Client:{Colors.RESET}  dist/RandevuGuest/RandevuGuest.exe")
        print(f"      {Colors.DIM}Paket: dist/RandevuGuest_v{SCRIPT_VERSION}.zip{Colors.RESET}")
    
    print(f"""
{Colors.YELLOW}📖 Dağıtım Kılavuzu:{Colors.RESET} dist/DEPLOYMENT_GUIDE.txt

{Colors.CYAN}🚀 Sıradaki Adımlar:{Colors.RESET}
   1. ZIP paketlerini ilgili bilgisayarlara kopyalayın
   2. .env dosyasını yapılandırın
   3. EXE dosyalarını çalıştırın

{Colors.DIM}© 2024 RandevuPy - Build Tarihi: {BUILD_DATE}{Colors.RESET}
""")
    
    input(f"\n{Colors.YELLOW}Kapatmak için ENTER'a basın...{Colors.RESET}")
    
    if results["admin"] or results["guest"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
