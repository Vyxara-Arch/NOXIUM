<div align="center">

<img src="assets/Noxium.png" width="360" alt="NOXIUM logo"/>

# NOXIUM
### Secure Vault - PQC Hybrid - Anti-Forensics - Windows Only

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](#)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#)
[![Status](https://img.shields.io/badge/Status-Beta%2FExperimental-ef4444?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-GPLv3-yellow?style=for-the-badge)](LICENSE)

</div>

---

## Обзор
- NOXIUM - настольное приложение для безопасных хранилищ, шифрования файлов и защищенных заметок.
- Поддерживаются современные алгоритмы (ChaCha20-Poly1305, AES-256-GCM, AES-256-SIV) и гибридный PQC-режим (Kyber через `pqcrypto`).
- Формат vault - бинарный (.vault) с обернутым ключом и шифрованным blob-контейнером.
- Интерфейс минималистичный, с темами, анимациями и понятными подсказками.

Важно: часть функций экспериментальная и может работать нестабильно. См. раздел **Beta / Experimental**.

---

## Интерфейс (основные экраны)
<table>
  <tr>
    <td width="50%">
      <h3>Dashboard</h3>
      <ul>
        <li>Сводка состояния системы (CPU/RAM)</li>
        <li>Статус активного хранилища и авто-лок</li>
        <li>Поиск по зашифрованному индексу</li>
        <li>Быстрые действия и журнал активности</li>
      </ul>
    </td>
    <td width="50%">
      <h3>Encryption Workspace</h3>
      <ul>
        <li>Очередь файлов и статистика</li>
        <li>Выбор алгоритма (Modern / Legacy)</li>
        <li>Сжатие, шредер, PQC</li>
        <li>Drag-and-drop файлов</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>Tools & Utilities</h3>
      <ul>
        <li>Steganography (PNG LSB)</li>
        <li>Ghost Link (SFTP)</li>
        <li>PassGen</li>
        <li>Secure Notes</li>
        <li>Folder Watcher</li>
      </ul>
    </td>
    <td width="50%">
      <h3>Settings</h3>
      <ul>
        <li>Алгоритмы по умолчанию</li>
        <li>Темы и визуальные акценты</li>
        <li>Auto-Lock и Device Lock</li>
        <li>Backups и Recovery Shares</li>
      </ul>
    </td>
  </tr>
</table>

---

## Функциональность

### Vault и безопасность
- Vault v2 (бинарный формат .vault) с обернутым ключом и шифрованным blob-контейнером.
- Автомиграция старых JSON-vault: конвертация + удаление JSON.
- 2FA (TOTP) и Duress Password.
- Сессии в памяти + авто-блокировка по таймеру.
- Audit Log для локальных событий (в памяти).

### Криптографический движок
- Файловое шифрование: ChaCha20-Poly1305, AES-256-GCM, AES-256-SIV.
- PQC Hybrid (Kyber): гибридный ключ через KEM + HKDF (опционально).
- KDF: Argon2id (основное), Scrypt (legacy blobs).
- Сжатие перед шифрованием (опционально).
- Legacy-decrypt: поддержка старых форматов (AES-SIV, Blowfish-CTR, CAST-CTR, ранние PQC-контейнеры).
- Secure Shredder (до 35 проходов). Важно: на SSD гарантий нет.

### Хранилище и данные
- Индексатор: in-memory SQLite + зашифрованный `index.db.enc`.
- Заметки: `.note` файлы с шифрованным содержимым.
- Бэкапы: `.vib` архивы, зашифрованные на экспорт/импорт.
- Файлы: `.ndsfc` для зашифрованных файлов.

### Инструменты и сеть
- Ghost Link (SFTP) с опциональным SOCKS5.
- Folder Watcher: авто-шифрование новых файлов в папке.
- Steganography: скрытие/извлечение данных в PNG.
- PassGen: генератор паролей с авто-очисткой буфера.

### UI/UX
- Light/Dark режимы и кастомные темы.
- Плавные переходы (FadeStack).
- Понятные подсказки и контекстные предупреждения.

---

## Legacy вкладка
В Encryption Settings есть отдельная вкладка **Legacy**.
- Алгоритмы там предназначены только для совместимости и не рекомендуются для новых данных.
- Используйте их только при необходимости восстановления старых архивов.

---

## Beta / Experimental
Некоторые функции находятся в бете и могут работать нестабильно:
- PQC Hybrid (Kyber) и связанная инфраструктура ключей.
- Steganography (скрытие в PNG).
- Ghost Link (SFTP) и SOCKS5 прокси.
- Folder Watcher (фоновый режим).
- Recovery Shares (Shamir-разделение ключа).
- Индексатор и поиск (in-memory + encrypted save).

---

## Форматы хранения
```
vaults/
  <vault>.vault           # бинарный vault v2
  <vault>/index.db.enc    # зашифрованный индекс
  <vault>/notes/*.note    # зашифрованные заметки
```

---

## Установка
```bash
git clone https://github.com/Vyxara-Arch/NOXIUM.git
cd NOXIUM
pip install -r requirements.txt
python main.py
```

---

## Требования
- Windows 10/11
- Python 3.10+
- Библиотеки из `requirements.txt`

---

## Авторы и вклад
```
MintyExtremum  - Core Cryptography
Vyxara-Arch    - Architecture & UI
Blooder        - Security Research & Testing
```

---

## Лицензия
GNU GPLv3. Приложение поставляется "как есть" без гарантий.

<div align="center">
NOXIUM - Leave Nothing Behind
</div>
