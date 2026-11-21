from dataclasses import dataclass, field

@dataclass 
class Flag:
    # DOES NOT NEED O(1) LOOKUP
    # DONT REMOVE name: str
    name: str
    description: str
    alternate_name: str = None # if the name is the short form, there's a long form 
    
    parameter: str = None
    required: bool = False

    def __str__(self):
        name = f"{self.name}, {self.alternate_name}" if self.alternate_name else self.name
        parameter_string = f"<{self.parameter}>"

        return f"{name} {parameter_string if self.parameter else ""}: {self.description} {"(required)" if self.required else ""}"
    

@dataclass
class CommandData:
    name: str
    description: str 
    parameters: tuple[str] = ()
    flags: tuple[Flag] = ()
    is_redirectable: bool = False

    flag_hashmap: dict[str, Flag] = field(init=False, repr=False, hash=False, compare=False)
    # not yet defined until __post_init__

    def __post_init__(self):
        self.flag_hashmap = {}
        
        if not self.flags:
            return None
        
        for flag in self.flags:
            self.flag_hashmap[flag.name] = flag

            if flag.alternate_name:
                self.flag_hashmap[flag.alternate_name] = flag


    def __str__(self):
        # basically the output of --help
        parameters_string = " ".join([f"<{parameter}>" for parameter in self.parameters]) if self.parameters else ""

        return f"{self.name} {parameters_string}\n{self.description}{"\nRedirectable: Yes" if self.is_redirectable else ""}\n{"\n".join(str(flag) for flag in self.flags)}{"\n" if self.flags else ""}" 


command_masterlist: dict[str, CommandData] = {}

# Unix Commands
command_masterlist["cd"] = CommandData(
    "cd",
    "Change the current working directory to DIRECTORY.",
    ("DIRECTORY",)
    # add commas here even if just a single entry 
    # otherwise, an iterator would loop over it as a string
)
command_masterlist["pwd"] = CommandData(
    "pwd",
    "Print the name of the current working directory.",
)
command_masterlist["mkdir"] = CommandData(
    "mkdir",
    "Create the DIRECTORY, if not already existing.",
    ("DIRECTORY",)
)
command_masterlist["ls"] = CommandData(
    "ls",
    "List information about the FILEs in the current directory.",
    flags=(
        Flag("-a", "do not ignore entries starting with ."),
        Flag("-s", "shows file \"size\" (character count)", "--size")
    ),
    is_redirectable=True
)
command_masterlist["touch"] = CommandData(
    "touch",
    "Creates FILE if not already existing.",
    ("FILE",)
)
command_masterlist["echo"] = CommandData(
    "echo",
    "Prints TEXT argument.",
    ("TEXT",),
    is_redirectable=True
)
command_masterlist["mv"] = CommandData(
    "mv",
    "Rename SOURCE to DESTINATION, or move SOURCE to DESTINATION.",
    ("SOURCE", "DESTINATION"),
)
command_masterlist["rm"] = CommandData(
    "rm",
    "Remove the FILE.",
    ("FILE",),
)
command_masterlist["rmdir"] = CommandData(
    "rmdir",
    "Remove the DIRECTORY if empty.",
    ("DIRECTORY",),
)

# Custom Commands
command_masterlist["print"] = CommandData(
    # not doing cat cause we're not gonna do multi-file arguments
    "print",
    "Prints the contents of the FILE argument.",
    ("FILE",),
    is_redirectable=True
)

command_masterlist["exit"] = CommandData(
    "exit",
    "End the shell session.",
)

command_masterlist["assess"] = CommandData(
    "assess",
    "Evaluate a .lush FILE or a raw EXPRESSION.",
    ("EXPRESSION",),
    is_redirectable=True
)

command_masterlist["explain"] = CommandData(
    "explain",
    "Show help for a COMMAND, or list all commands with -a.",
    ("COMMAND",),
    flags=(
        Flag("-a", "list all available commands", "--all"),
    ),
)

command_masterlist["selfdestruct"] = CommandData(
    "selfdestruct",
    "WARNING: Will ANNIHILATE the entire filesystem.",
    ("PASSWORD",),
    # flags=(
    #     Flag("-t", "set a timer", "--time", parameter="TIME"),
    # ),
)

command_masterlist["save"] = CommandData(
    "save",
    "Save the filesystem to storage.",
)

command_masterlist["makenames"] = CommandData(
    "makenames",
    "Generate random names.",
    flags=(
        Flag("-g", "gender: feminine|masculine|unisex", "--gender", parameter="GENDER"),
        Flag("-f", "name format: given|surname", "--name-format", parameter="FORMAT"),
        Flag("-m", "middle name display: abbr|full|none", "--middle-name", parameter="MODE"),
        Flag("-N", "amount (default 50) ", "--amount", parameter="AMOUNT"),
    ),
    is_redirectable=True
)

command_masterlist["namehunt"] = CommandData(
    "namehunt",
    "Fun way to crash your terminal. Prints names until your target is hit.",
    flags=(
        Flag("-g", "target given name", "--given", parameter="GIVEN", required=True),
        Flag("-s", "target surname", "--surname", parameter="SURNAME", required=True),
        Flag("-m", "target middle name or initial", "--middle", parameter="MIDDLE"),
        Flag("-x", "target extension: Jr.|Sr.|I|II|III|IV", "--extension", parameter="EXTENSION"),
    ),
    is_redirectable=True
)

command_masterlist["gwac"] = CommandData(
    "gwac",
    "GWA calculator. Reads grades from a FILE or through inputs.",
    flags=(
        Flag("-f", "read grades from FILE", "--file", parameter="FILE"),
    ),
    is_redirectable=True
)

# [print(command[1], "\n") for command in sorted(command_masterlist.items())]


