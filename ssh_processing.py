sep = "\n"
tab = "\t"

parameters = {
    "PubkeyAuthentication":
        {
            "type": "boolean",
            "default": "yes",
            "description": f"Авторизация по ключу."
        },
    "PasswordAuthentication":
        {
            "type": "boolean",
            "default": "no",
            "description": "Авторизация по паролю."
        },
    "PermitRootLogin":
        {
            "type": "boolean",
            "default": "no",
            "description": "Разрешить вход root."
        },
    "MaxAuthTries":
        {
            "type": "number",
            "default": "3",
            "description": "Максимальное количество попыток авторизации."
        },
    "LoginGraceTime":
        {
            "type": "text",
            "default": "60s",
            "description": "Время ожидания после попытки авторизации."
        },
    "X11Forwarding":
        {
            "type": "boolean",
            "default": "no",
            "description": "Разрешить X11-форвардинг."
        },
    "AllowTcpForwarding":
        {
            "type": "boolean",
            "default": "no",
            "description": "Разрешить TCP-форвардинг."
        },
    "AllowAgentForwarding":
        {
            "type": "boolean",
            "default": "no",
            "description": "Разрешить агент-форвардинг."
        },
    "port":
        {
            "type": "number",
            "default": "22",
            "description": "Порт SSH."
        },
    "ClientAliveInterval":
        {
            "type": "number",
            "default": "300",
            "description": "Интервал проверки активности клиента."
        },
    "ClientAliveCountMax":
        {
            "type": "number",
            "default": "2",
            "description": "Максимальное количество проверок активности клиента."
        },
    "StrictModes":
        {
            "type": "boolean",
            "default": "yes",
            "description": "Строгие режимы."
        }
}

header = """Include /etc/ssh/ssh_config.d/*.conf

Host *
\t"""

default_parameters = f"Параметры по умолчанию: \n{'=' * 60}\n{sep.join([tab.join([key, parameters[key]['default'], ' - ', parameters[key]['description']]) for key in parameters.keys()])}\n{'=' * 60}\n"


class ProcessingConfigFile:

    def __init__(self):
        self.params = parameters

        if input(default_parameters + "Настроить по умолчанию? (y/n) - ").lower() == "y":
            self.generate_config_file_with_params()
        else:
            self.refactoring_config_file()

    def generate_config_file_with_params(self):
        with open("ssh_config", "w") as file:
            file.write(header)
            file.write((sep + tab).join(
                [" ".join([key, self.params[key]['default'], ' #', self.params[key]['description']]) for key in
                 self.params.keys()])
            )
    def refactoring_config_file(self):
        with open("ssh_config", "w") as file:
            file.write(header)
            for key in self.params.keys():
                if input(f"Параметр по умолчанию - {key} {self.params[key]['default']}\tизменить? (y/n) - ").lower() == "y":
                    self.params[key]['default'] = input(f"Введите значение для параметра {key} - ")
            file.write((sep + tab).join(
                [" ".join([key, self.params[key]['default'], ' #', self.params[key]['description']]) for key in
                 self.params.keys()])
            )

