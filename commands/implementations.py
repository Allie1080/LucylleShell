from dataclasses import dataclass, field
import shlex

import time

from commands.data import command_masterlist, CommandData, Flag
from filesystem import FileSystem

from my_libraries.Name_Generator.main import play_name_hit, run_name_generator
from my_libraries.GWA_Calculator.main import calculate_GWA, calculate_total_units, collect_grade_data, read_from_input

# scope of this project only allows redirects, not piping

REDIRECT_WRITE_SYMBOL = ">"
REDIRECT_APPEND_SYMBOL = ">>"

REDIRECT_SYMBOLS = {REDIRECT_APPEND_SYMBOL, REDIRECT_WRITE_SYMBOL}

ERROR_INVALID_COMMAND = SyntaxError("No such command found")
ERROR_INVALID_FLAG = SyntaxError("Invalid flag in command")
ERROR_MISSING_FLAG_ARGUMENT = SyntaxError("A flag is missing an argument")
ERROR_INVALID_REDIRECT = SyntaxError("Invalid redirect target")

ERROR_LS_PATH_NOT_IMPLEMENTED = SyntaxError("Does not take arguments yet")

ERROR_EXPLAIN_NO_ARGUMENT = SyntaxError("No command to explain")

ERROR_MAKENAMES_INVALID_AMOUNT = SyntaxError("Amount must be a positive integer")

ERROR_ASSESS_NO_ARGUMENT = SyntaxError("Nothing to assess")

ERROR_SELFDESTRUCT_MISSING_PASSWORD = SyntaxError("Missing password")
ERROR_SELFDESTRUCT_INCORRECT_PASSWORD = SyntaxError("Incorrect password")
ERROR_SELFDESTRUCT_INVALID_TIME = SyntaxError("Armed timer must be a positive integer")

_SELFDESTRUCT_PASSWORD = "armed_67"


@dataclass
class ParsedInput:
    name: str
    arguments: tuple[str]
    flags: dict[str, str] = field(default_factory=dict)
    redirect_target: tuple[str, bool] = ()
    # True if redirect is append


def _parse_flag() -> tuple[bool, bool]:
    pass


def _find_command(command_masterlist: dict[str, CommandData], command_name) -> CommandData:
    try: 
        return command_masterlist[command_name]

    except KeyError:
        raise ERROR_INVALID_COMMAND 
                    

def _find_command_flag(flag_hashmap: dict[str, Flag], provided_flag: str) -> Flag:
    try:
        return flag_hashmap[provided_flag]
    
    except KeyError:
        raise ERROR_INVALID_FLAG

# returns command_chain, None if not found, has True if redirect is append
def _separate_redirect_chain(command_chain: list[str]) -> tuple[list[str], tuple[str, bool]]:
    for index, value in enumerate(command_chain):
        # TIL, sets offer much faster performance for this kind of operation
        # consumes more RAM tho, ig
        if value in REDIRECT_SYMBOLS:
            if index != len(command_chain) - 2:
                raise ERROR_INVALID_REDIRECT

            return command_chain[:index], (command_chain[-1], value == REDIRECT_APPEND_SYMBOL) 

    return command_chain, None

# parses flags for appropriate parameters too
# though it works by blindly adding the next component if a parameter is found
# currently doesn't parse missing required flags 
def _separate_flags_and_arguments(command_chain: list[str], flag_hashmap: dict[str, Flag]) -> tuple[dict[str, str], list[str]]:
    provided_flags: dict[str, str] = {}
    provided_arguments: list[str] = []
    
    component_index = 1  # skip command name
    while component_index < len(command_chain):
        component = command_chain[component_index]
        
        if not component.startswith("-"):
            provided_arguments = command_chain[component_index:]
            break

        flag = _find_command_flag(flag_hashmap, component)
        # raises error if component isn't a flag

        if flag.parameter:
            component_index += 1

            if component_index >= len(command_chain):
                raise ERROR_MISSING_FLAG_ARGUMENT
            
            provided_flags[flag.name] = command_chain[component_index]
        
        else:
            provided_flags[flag.name] = True # has to be true, otherwise key wont be added

        component_index += 1


    return provided_flags, provided_arguments

def parse_command(command: str) -> ParsedInput:
    provided_name: str
    provided_arguments: list[str] 
    provided_flags: dict[str, str] = {}
    redirect_target: tuple[str, bool] = ()

    command_data: CommandData
        
    command_chain = shlex.split(command)

    provided_name = command_chain[0]
    command_data = _find_command(command_masterlist, provided_name)
    # raises error if command isn't found

    command_chain, redirect_data = _separate_redirect_chain(command_chain)
    provided_flags, provided_arguments = _separate_flags_and_arguments(command_chain, command_data.flag_hashmap)

    return ParsedInput(
        provided_name,
        provided_arguments,
        provided_flags,
        redirect_data
    )

# Unix Commands

def cd(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    filesystem.change_directory(parsed_command.arguments[0])


def pwd(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    return filesystem.get_working_directory()


def mkdir(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    filesystem.make_directory(parsed_command.arguments[0])


def ls(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    entries: list[str]
    show_all: bool
    show_size: bool
    result_lines: list[str] = []


    if parsed_command.arguments:
        raise ERROR_LS_PATH_NOT_IMPLEMENTED
    
    entries = list(filesystem.list_directory("."))

    show_all = "-a" in parsed_command.flags
    show_size = "-s" in parsed_command.flags


    for entry in sorted(entries):
        if not show_all and entry.startswith("."):
            continue

        if show_size:
            if entry.endswith("/"):
                result_lines.append(f"[D] {entry}")
            
            else:
                try:
                    content = filesystem.view_file(entry)
                    result_lines.append(f"[{len(content)}] {entry}")
                
                except SyntaxError:
                    result_lines.append(f"[?!!] {entry}")

        else:
            result_lines.append(entry)

    return "\n".join(result_lines)


def touch(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    filesystem.create_file(parsed_command.arguments[0])


def echo(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    return " ".join(parsed_command.arguments)


def mv(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    filesystem.move_file(parsed_command.arguments[0], parsed_command.arguments[1])


def rm(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    filesystem.delete_file(parsed_command.arguments[0])


def rmdir(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    filesystem.delete_empty_directory(parsed_command.arguments[0])


def exit_command(filesystem: FileSystem, parsed_command: ParsedInput) -> None:
    exit(1)


# Lucylle Originals

# print doesn't concatenate files like cat
def print_file(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    return filesystem.view_file(parsed_command.arguments[0])


def assess(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    if not parsed_command.arguments:
        raise ERROR_ASSESS_NO_ARGUMENT

    first_argument = parsed_command.arguments[0]

    if len(parsed_command.arguments) == 1 and first_argument.endswith(".lush"):
        expression = filesystem.view_file(first_argument)
    
    else:
        expression = " ".join(parsed_command.arguments)

    try:
        return str(eval(expression, {"__builtins__": {'print': print, 'range': range}}, {}))
    
    except Exception as error:
        raise SyntaxError(error)

def explain(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    if "-a" in parsed_command.flags:
        return "\n".join(sorted(command_masterlist.keys()))

    if not parsed_command.arguments:
        raise ERROR_EXPLAIN_NO_ARGUMENT

    command_name = parsed_command.arguments[0]
    command_data = command_masterlist.get(command_name)

    if command_data is None:
        raise ERROR_INVALID_COMMAND

    return str(command_data)


def selfdestruct(filesystem: FileSystem, parsed_command: ParsedInput):
    if not parsed_command.arguments:
        raise ERROR_SELFDESTRUCT_MISSING_PASSWORD

    if parsed_command.arguments[0] != _SELFDESTRUCT_PASSWORD:
        raise ERROR_SELFDESTRUCT_INCORRECT_PASSWORD

    # if "-t" in parsed_command.flags:
    #     time_string = parsed_command.flags["-t"]

    #     if not time_string.isdigit():
    #         raise ERROR_SELFDESTRUCT_INVALID_TIME
        
    #     elif int(time_string) <= 0:
    #         # avoids a ValueError
    #         raise ERROR_SELFDESTRUCT_INVALID_TIME

    #     ultimatum = time.time() + int(time_string)
    #     filesystem.set_time_to_destruction(ultimatum)

    #     return f"Self-Destruct Armed. Annihilation in {time_string} seconds."

    filesystem.annihilate()
    return "Annihilation."


def save(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    filesystem.save_to_storage(filesystem._default_storage_name)
    
    return "Session saved."

def makenames(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    gender = parsed_command.flags.get("-g", "feminine")
    amount_string = parsed_command.flags.get("-N", "50")
    amount: int

    if not amount_string.isdigit():
        raise ERROR_MAKENAMES_INVALID_AMOUNT

    amount = int(amount_string)
    
    if amount <= 0:
        raise ERROR_MAKENAMES_INVALID_AMOUNT

    format_map = {
        "given": "standard",
        "surname": "surname_first_standard",
    }
    name_format = format_map.get(parsed_command.flags.get("-f", "given"), "standard")

    generated_text = run_name_generator(
        name_gender=gender,
        name_format=name_format,
        amount=amount,
        disable_joke_names=False,
        delay_in_seconds=0,
        print_names=False # the shell prints it itself
    )

    return generated_text

def namehunt(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    given_name = parsed_command.flags.get("-g")
    surname = parsed_command.flags.get("-s")
    middle_name = parsed_command.flags.get("-m")
    extension = parsed_command.flags.get("-x")

    if not given_name:
        raise ERROR_MISSING_FLAG_ARGUMENT

    if not surname:
        raise ERROR_MISSING_FLAG_ARGUMENT

    return play_name_hit(
        target_given_name=given_name,
        target_surname=surname,
        target_middle_name=middle_name,
        target_extension=extension,
        print_names=True,
    )

def gwac(filesystem: FileSystem, parsed_command: ParsedInput) -> str:
    file_name = parsed_command.flags.get("-f")

    if file_name:
        content = filesystem.view_file(file_name)
        
        grades_reader = [[cell.strip() for cell in line.split(",")] for line in content.splitlines() if line.strip()]
        
        grades_list = collect_grade_data(grades_reader)

        if not grades_list:
            return "No grades found."

        gwa = calculate_GWA(grades_list)
        unit_total = calculate_total_units(grades_list)

        lines = [f"GWA: {gwa:.2f}", f"Unit Total: {unit_total}", "", "Grades:"]
        for grade in grades_list:
            lines.append(f"{grade.raw:.2f} - {grade.units} unit/s")

        return "\n".join(lines)

    else:
        return read_from_input()


command_handlers = {
    "cd": cd,
    "pwd": pwd,
    "mkdir": mkdir,
    "ls": ls,
    "touch": touch,
    "echo": echo,
    "mv": mv,
    "rm": rm,
    "rmdir": rmdir,
    "exit": exit_command,
    "print": print_file,
    "assess": assess,
    "explain": explain,
    "selfdestruct": selfdestruct,
    "save": save,
    "makenames": makenames,
    "namehunt": namehunt,
    "gwac": gwac,
}