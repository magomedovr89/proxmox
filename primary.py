#!/usr/bin/env python3
"""
Скрипт для установки программ на операционную систему Debian
Устанавливает: ufw, sudo, openssh-server, ssh
Включает обновление пакетов перед установкой
"""

import subprocess
import sys
import os

import ssh_processing
from datetime import datetime


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
    """Выводит отчет о результатах установки пакетов
    packages: list[str] - список установленных пакетов
    failed_packages: list[str] - список неустановленных пакетов"""

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
    packages = ['ufw', 'sudo', 'openssh-server', 'ssh', "mc", "htop"]

    print(f"[INFO] Будут установлены следующие пакеты: {', '.join(packages)}")

    # 1. Обновление списка пакетов
    if input("Обновить список пакетов? (y/n): ").lower() != "y":

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

    # 5.Настройка UFW
    if input("Настроим UFW? (y/n): ").lower() == "y":
        if not run_command("ufw enable", "Включение UFW"):
            print("[WARNING] Не удалось включить UFW")
            exit(1)
        else:
            print("[INFO] Настройка UFW:")
            ports = input("Введите порты для открытия через UFW (пример: 22 80 443): ").split()
            for port in ports:
                run_command(f"ufw allow {port}", f"Разрешение порта {port}")
        print("Проверка UFW")
        if not run_command("ufw status verbose", "Проверка UFW"):
            print("[WARNING] Не удалось включить UFW")
            exit(1)
    # 6. Настройка SSH
    if input("Настроим SSH? (y/n): ").lower() == "y":
        ssh_processing.ProcessingConfigFile()
        if input("Внести изменения в систему (y/n) - ").lower() == "y":
            if not run_command("mkdir -p /etc/ssh/backup", "Создание директории для бэкапа SSH конфигурации"):
                print("[WARNING] Не удалось создать директорию для бэкапа SSH конфигурации")
            print("=" * 60)
            if not run_command(
                    f"cp /etc/ssh/sshd_config /etc/ssh/backup/ssh_config_{datetime.now().strftime('%Y_%m_%d_%H_%M')}",
                    "Бэкап SSH конфигурации"):
                print("[WARNING] Не удалось создать бэкап SSH конфигурации")
        else:
            print("Внесите изменения в SSH конфигурации вручную")
            print("Файл находится в директории backup")
            print("=" * 60)
    print("=" * 60)
    if input("Настроим sudo? (y/n) - ").lower() == "y":
        user = input("Введите имя пользователя - ")
        if input("Создать пользователя? (y/n) - ").lower() == "y":
            os.system(f"adduser {user}")
        os.system(f"usermod -aG sudo {user}")
        os.system(f"/etc/sudoers.d/{user}")
        with open(f"/etc/sudoers.d/{user}", "w") as file:
            file.write(f"{user} ALL=(ALL) NOPASSWD:ALL")
        print(f"sudo настройки для пользователя {user} созданы")
    print("=" * 60)
    print("  1. Настройте пользователей для sudo: usermod -aG sudo <username>")
    print("  2. Настройте SSH ключи для безопасного доступа")


if __name__ == "__main__":
    main()
