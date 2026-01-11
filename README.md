<div align="center">

<img src="assets/ndsfc_splash.png" width="720"/>

# 🛡️ NDSFC v2.0  
## The Digital Fortress  
### *Titanium-Grade Privacy · Anti-Forensics · Post-Quantum Encryption*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Security-Zero--Persistence-critical?style=for-the-badge&logo=shield&logoColor=white)](#)
[![Crypto](https://img.shields.io/badge/Crypto-Post--Quantum-orange?style=for-the-badge)](#)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-GPLv3-yellow?style=for-the-badge)](LICENSE)

**NDSFC** is an advanced digital security suite focused on  
**deniable encryption**, **forensic invisibility**, and **absolute data sovereignty**.

Designed for hostile environments.

---

[ 🇺🇸 English ](#english) · [ 🇷🇺 Русский ](#russian) · [ 🇨🇳 中文 ](#chinese)

</div>

---

<a name="english"></a>
## 🇺🇸 English — Technical Overview

### 🔐 Core Security Philosophy — *Zero Persistence*
Encryption alone is insufficient.  
**True security means leaving no trace.**

NDSFC enforces:
- No plaintext artifacts on disk
- No persistent encryption keys
- No recoverable metadata

All cryptographic material exists **only in volatile RAM** and is securely wiped after use.

---

### ⚛️ Cryptographic Engine (v2.0)

| Component | Description |
|---------|-------------|
| **Post-Quantum Cascade** | Hybrid encryption using `AES-256-GCM` + `ChaCha20-Poly1305` |
| **Deterministic Encryption** | `AES-SIV` — safe under IV reuse |
| **KDF** | `Scrypt` + `Argon2` (high memory cost) |
| **Hashing** | `SHA3-512` |
| **Legacy Support** | Blowfish-CTR, CAST5-CTR |

> **IMPORTANT:** All algorithms are implemented with explicit zero-memory cleanup.

---

### 🧠 Strategic Modules

#### 📂 Mission Control
- Encrypted SQLite index (metadata only)
- Lightning-fast global search
- Vault & session monitoring

#### 🛡️ Stealth & Anti-Forensics
- **Duress Password** → silent index annihilation
- **RAM-only sessions**
- **Steganography 2.0** (PNG LSB matching)
- **DoD 5220.22-M Shredder** (up to 35 passes)

#### 🧰 Omega Tools
- **Ghost Link (SFTP)** — encrypted remote vault transfer
- **Folder Watcher** — auto-encryption on file drop
- **Secure Journal** — encrypted markdown notes
- **`.vib` Vault Integrity Backups**

---

### 📊 Monitoring & Runtime Safety

- Real-time memory consumption
- Session lifespan tracking
- Encryption task status
- Index integrity checks

> ⚠️ If the process crashes — **keys die with RAM**

---

### 🏗️ Project Architecture
NDSFC/
├── core/
│ ├── crypto_engine.py
│ ├── indexer.py
│ ├── auth.py
│ ├── vault_manager.py
│ ├── folder_watcher.py
│ ├── notes_manager.py
│ ├── backup_manager.py
│ └── shredder.py
├── gui/
│ └── app_qt.py
├── vaults/
└── main.py

---

<a name="russian"></a>
## 🇷🇺 Русский — Полная спецификация

### 🔒 Философия — *Нулевой След*
**NDSFC v2.0** создан для ситуаций, где компромисс невозможен.

- Никаких следов на диске  
- Никаких ключей после выхода  
- Никакой возможности восстановления  

---

### 🚨 Критически важно
> ❗ Потеря мастер-пароля или 2FA = **полная и необратимая потеря данных**

Проект **НЕ содержит бэкдоров**.

---

### 🚀 Возможности
- Глобальный зашифрованный поиск
- Пароль принуждения (panic mode)
- Стеганография без визуальных артефактов
- Мульти-хранилища
- Pre-Glassmorphism V1.5 UI

---

<a name="chinese"></a>
## 🇨🇳 中文 — 技术概览

### 🔐 核心理念：零持久性
NDSFC 采用 **零痕迹安全模型**：
- 加密密钥仅存在于内存中
- 无磁盘残留
- 无法取证恢复

---

### 🛡️ 安全功能
- 后量子混合加密
- 强抗暴力破解 KDF
- 恐慌密码（静默销毁）
- 隐写存储（PNG）

> **注意：** 一旦密钥丢失，数据将永久无法恢复。

---

## 🛠️ Installation

```bash
git clone https://github.com/Vyxara-Arch/NDSFC.git
cd NDSFC
pip install -r requirements.txt
python main.py
```


👥 Authors & Contributors
MintyExtremum — Core Cryptography
Vyxara-Arch — Architecture & UI
Blooder — Security Research & Testing & README

---

📜 License 
GNU GPLv3. This software is provided AS IS. Use responsibly. Freedom requires responsibility. check `LICENSE` for details.

---

<div align="center">
🔐 NDSFC — when privacy must survive anything.
</div>
