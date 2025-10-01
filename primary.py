#!/usr/bin/env python3
"""
Скрипт для установки программ на операционную систему Debian
Устанавливает: ufw, sudo, openssh-server, ssh
Включает обновление пакетов перед установкой
"""

import subprocess
import sys
import os


def run_command(command: str, description: str) -> bool:
    """Выполняет команду в командной строке с обработкой ошибок
    и вывода результата
    command: str - команда для выполнения
    description: str - описание команды для вывода в консоль"""
    print(f"\n[INFO] {description}")
    print(f"[CMD] {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"[SUCCESS] {description} выполнено успешно")
        if result.stdout:
            print(f"[OUTPUT] {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при выполнении: {description}")
        print(f"[ERROR] Код ошибки: {e.returncode}")
        if e.stderr:
            print(f"[ERROR] {e.stderr}")
        return False


def check_root_privileges() -> None:
    """Проверяет, запущен ли скрипт с правами root"""
    if os.geteuid() != 0:
        print("[ERROR] Скрипт должен быть запущен с правами root (sudo)")
        print("[INFO] Запустите: sudo python3 install_packages.py")
        sys.exit(1)


def print_report(packages: list[str], failed_packages: list[str]) -> None:
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)

    print("\n[INFO] Установленные пакеты:")
    for package in packages:
        if package not in failed_packages:
            print(f"  ✓ {package}")
        else:
            print(f"  ✗ {package} (ошибка установки)")
    if failed_packages:
        print(f"[WARNING] Следующие пакеты не удалось установить: {', '.join(failed_packages)}")
    else:
        print("[SUCCESS] Все пакеты установлены успешно!")


def main():
    """Основная функция установки пакетов"""
    print("=" * 60)
    print("СКРИПТ УСТАНОВКИ ПАКЕТОВ ДЛЯ DEBIAN")
    print("=" * 60)

    # Проверка прав root
    check_root_privileges()

    # Список пакетов для установки
    packages = ['ufw', 'sudo', 'openssh-server', 'ssh', "mc"]

    print(f"[INFO] Будут установлены следующие пакеты: {', '.join(packages)}")

    # 1. Обновление списка пакетов
    if not run_command("apt update", "Обновление списка пакетов"):
        print("[ERROR] Не удалось обновить список пакетов")
        sys.exit(1)

    # 2. Обновление установленных пакетов
    if input("Обновить установленные пакеты? (y/n): ").lower() != "y":
        if not run_command("apt upgrade -y", "Обновление установленных пакетов"):
            print("[WARNING] Обновление пакетов завершилось с ошибками")

    # 3. Установка каждого пакета
    failed_packages = []

    for package in packages:
        command = f"apt install -y {package}"
        if not run_command(command, f"Установка пакета {package}"):
            failed_packages.append(package)

    # 4. Итоговый отчет
    print_report(packages, failed_packages)

    print("\n[INFO] Рекомендуемые следующие шаги:")
    print("  1. Настройте пользователей для sudo: usermod -aG sudo <username>")
    print("  2. Настройте SSH ключи для безопасного доступа")
    print("  3. Проверьте настройки UFW: ufw status verbose")


if __name__ == "__main__":
    main()
