import time

from commands.implementations import command_handlers, parse_command
from filesystem import FileSystem

from commands.data import command_masterlist


PROMPT = "\033[31mlush> \033[0m"


class ShellErrorHandler:
    @staticmethod
    def invalid_command(command_name: str) -> str:
        return f"No such command: {command_name}"

    @staticmethod
    def not_redirectable(command_name: str) -> str:
        return f"{command_name}: Not redirectable"

    @staticmethod
    def command_error(command_name: str, error: str) -> str:
        return f"{command_name}: {error}"

    @staticmethod
    def redirect_error(error: str) -> str:
        return f"Redirect: {error}"


def print_error(message: str) -> None:
    # what to format...
    print(message)


# def check_selfdestruct(filesystem: FileSystem) -> None:
#     destruction_time = filesystem.get_time_to_destruction()

#     if destruction_time is None:
#         return

#     if time.time() < destruction_time:
#         return

#     filesystem.annihilate()
#     filesystem.set_time_to_destruction(None)
    
#     print("Annihilation")


def run_shell(filesystem: FileSystem) -> None:

    while True:
        # check_selfdestruct(filesystem)

        try:
            raw_input = input(PROMPT)
        
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw_input.strip():
            continue

        try:
            parsed_command = parse_command(raw_input)


        except SyntaxError as error:
            print_error(str(error))
            continue

        if parsed_command.redirect_target:
            command_data = command_masterlist.get(parsed_command.name)

            if command_data is None or not command_data.is_redirectable:
                print_error(ShellErrorHandler.not_redirectable(parsed_command.name))
                continue

        handler = command_handlers.get(parsed_command.name)

        if handler is None:
            print_error(ShellErrorHandler.invalid_command(parsed_command.name))
            continue

        try:
            output = handler(filesystem, parsed_command)

        except SyntaxError as error:
            print_error(ShellErrorHandler.command_error(parsed_command.name, str(error)))
            continue

        if output is None:
            continue

        if parsed_command.redirect_target:
            target, is_append = parsed_command.redirect_target

            try:
                if is_append:
                    filesystem.append_to_file(output, target)
                else:
                    filesystem.write_to_file(output, target)

            except SyntaxError as error:
                print_error(ShellErrorHandler.redirect_error(str(error)))

        else:
            print(output)
