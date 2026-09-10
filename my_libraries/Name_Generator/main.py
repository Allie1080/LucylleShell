import random
import csv
import pathlib
import time


ENCODING = "utf-8"
MODULE_DIRECTORY = pathlib.Path(__file__).parent
NAMES_FILE_PATH = MODULE_DIRECTORY / "names.csv"

EXTENSIONS = ["Jr.", "Sr.", "II", "III", "IV"]
JOKE_NAMES = ["Javascript", "C++", "Fortran", "Haskell", "Cobol"]

TYPES_NUMERIC = {
    "surname": 0,
    "feminine": 1,
    "masculine": 2,
    "unisex": 3,
}

EMAIL_PROVIDERS = ["gmail", "protonmail", "outlook", "yahoo", "mail"]


def load_names_lists() -> list[list[str]]:
    with open(NAMES_FILE_PATH, "r", encoding=ENCODING) as names_file:
        return list(csv.reader(names_file))


NAMES_LISTS = load_names_lists()


class FullName:
    def __init__(self, given_name: str, surname: str, middle_name: str = None, extension: str = None):
        self.given = given_name
        self.middle = middle_name
        self.surname = surname
        self.extension = extension

    def join_names(self, *names: str) -> str:
        joined_name = ""
        
        for name in names:
        
            if name is None:
                continue
            joined_name += name + " "
        
        return joined_name.strip()

    def to_string(self, type="standard") -> str:
        if type == "standard":
            return self.join_names(self.given, self.middle[0].upper() + "." if self.middle else None, self.surname, self.extension)
        
        elif type == "full":
            return self.join_names(self.given, self.middle if self.middle else None, self.surname)
        
        elif type == "surname_first_standard":
            return self.join_names(self.surname + ",", self.given, self.middle[0].upper() + "." if self.middle else None)
        
        elif type == "surname_first_full":
            return self.join_names(self.surname + ",", self.given, self.middle if self.middle else None, self.extension)
        
        else:
            return "Unknown Type"


def print_row(items, row_width: int = 40) -> None:
    for item in items:
        print(item + (" " * (row_width - len(item))), end="")
    
    print()


def get_chance_bool(numerator: int, denominator: int = 10) -> bool:
    return random.randint(1, denominator) <= numerator


def get_single_random_name(name_type: str = "feminine", disable_joke_name: bool = True) -> str:
    raw_list = NAMES_LISTS[TYPES_NUMERIC[name_type]][1:]
    cleaned_list = [name.strip() for name in raw_list if name.strip()]

    if name_type != "surname":
        unisex_raw = NAMES_LISTS[3][1:]
        cleaned_list.extend([name.strip() for name in unisex_raw if name.strip()])

    name = cleaned_list[random.randint(0, len(cleaned_list) - 1)]

    if disable_joke_name and name in JOKE_NAMES:
        return get_single_random_name(name_type, disable_joke_name)
    
    return name


def generate_name(name_gender: str = "feminine", disable_joke_name: bool = True) -> FullName:
    given_name_count = 1 if get_chance_bool(3) else 2 if get_chance_bool(8) else 3

    given_name = [get_single_random_name(name_gender, disable_joke_name) for _ in range(given_name_count)]

    if given_name[0] == "Maria" and len(given_name) > 1:
        given_name[0] = "Ma." if get_chance_bool(4) else "Maria"

    given_name = " ".join(given_name)

    surname_count = 1 if get_chance_bool(9) or name_gender == "masculine" else 2
    surname = "-".join(get_single_random_name("surname", disable_joke_name) for _ in range(surname_count))

    middle_name = get_single_random_name("surname", disable_joke_name) if get_chance_bool(8) else None
    extension = EXTENSIONS[random.randint(0, len(EXTENSIONS) - 1)] if get_chance_bool(1) and name_gender == "masculine" else None

    return FullName(given_name, surname, middle_name, extension)


def generate_email_and_password(full_name: FullName, minimum_email_length: int = 5) -> tuple[str, str]:
    random.seed(full_name.to_string())

    email = ""
    password = ""
    given_names = full_name.given.split(" ")

    abbreviate_surname = bool(random.randint(0, 1))
    use_periods = get_chance_bool(7)
    password_method = random.randint(0, 2)
    random_given_name = given_names[random.randint(0, len(given_names) - 1)]

    if len(given_names) == 1:
        if abbreviate_surname:
            email += given_names[0].lower()
        else:
            email += given_names[0][0].lower()
        if use_periods:
            email += "."
    
    elif len(given_names) > 1 and not abbreviate_surname:
        for name in given_names:
            email += name[0].lower()
            email += "." if use_periods else ""
    
    elif len(given_names) > 1 and abbreviate_surname:
        email += random_given_name.lower()
        email += "." if use_periods else ""

    if abbreviate_surname and use_periods and full_name.middle:
        email += full_name.middle[0].lower() + "."

    if abbreviate_surname:
        email += full_name.surname[0].lower()
   
    else:
        if use_periods:
            email += full_name.surname.replace("-", ".").replace(" ", ".").lower()
        else:
            email += full_name.surname.replace("-", "").replace(" ", ".").lower()

    if len(email) < minimum_email_length or use_periods:
        for _ in range(minimum_email_length - random.randint(0, minimum_email_length // 2)):
            email += f"{random.randint(0, 9)}"

    email += f"@{EMAIL_PROVIDERS[random.randint(0, len(EMAIL_PROVIDERS) - 1)]}.com"

    if password_method == 0:
        password += random_given_name.lower() + "123"
   
    elif password_method == 1:
        password += full_name.surname.split("-")[0].lower().replace(" ", "") + "123"
   
    elif password_method == 2:
        password += (random_given_name + full_name.surname.split("-")[0]).lower().replace(" ", "").replace("o", "0").replace("i", "!" if random.randint(0, 1) else "1").replace("e", "3").replace("g", "9")

    return (email, password)


def run_name_generator(
    name_gender: str = "feminine",
    name_format: str = "standard",
    amount: int = 50,
    disable_joke_names: bool = True,
    include_email_and_password: bool = True,
    delay_in_seconds: float = 0.1,
    record_time: bool = False,
    print_names: bool = True,
    output_filename: str = None,
) -> str:
    is_any_gender = False
    lines: list[str] = []

    if record_time:
        time_start = time.time()

    if name_gender == "any_gender":
        is_any_gender = True
        name_gender = "feminine" if random.randint(0, 1) == 0 else "masculine"

    for _ in range(amount):
        full_name = generate_name(name_gender, disable_joke_names)
        formatted_name = full_name.to_string(name_format)

        if include_email_and_password:
            email, password = generate_email_and_password(full_name)
            line = ", ".join([formatted_name, email, password])
        else:
            line = formatted_name

        lines.append(line)
        if print_names:
            print(line)

        if is_any_gender:
            name_gender = "feminine" if random.randint(0, 1) == 0 else "masculine"

        if delay_in_seconds > 0:
            time.sleep(delay_in_seconds)

    if output_filename:
        with open(output_filename, "w", encoding=ENCODING) as output_file:
            output_file.write("\n".join(lines))

    if record_time:
        print(f"Duration: {time.time() - time_start}s")

    return "\n".join(lines)


def play_name_hit(
    target_given_name: str,
    target_surname: str = None,
    target_middle_name: str = None,
    target_extension: str = None,
    max_iterations: int = 10000000,
    print_names: bool = True,
) -> str:
    given_name_hit_count = 0
    surname_hit_count = 0
    middle_name_hit_count = 0
    extension_hit_count = 0
    given_name_and_surname_hit_count = 0
    name_without_extension_hit_count = 0
    name_count = 0

    while name_count < max_iterations:
        name = generate_name()
        name_count += 1

        if print_names:
            print(f"{name_count} {name.to_string()}")

        given_match = name.given == target_given_name
        surname_match = target_surname is None or name.surname == target_surname
        middle_match = target_middle_name is None or name.middle == target_middle_name
        extension_match = target_extension is None or name.extension == target_extension

        if name.given == target_given_name:
            given_name_hit_count += 1
       
        if target_surname and name.surname == target_surname:
            surname_hit_count += 1
       
        if target_middle_name and name.middle == target_middle_name:
            middle_name_hit_count += 1
       
        if target_extension and name.extension == target_extension:
            extension_hit_count += 1

        if given_match and surname_match:
            given_name_and_surname_hit_count += 1
       
        if given_match and surname_match and middle_match:
            name_without_extension_hit_count += 1

        if given_match and surname_match and middle_match and extension_match:
            print("Hit! Hit! Hit!")
            break

    stats_lines = [
        f"Total Names Generated: {name_count}",
        f"Given Name Matches: {given_name_hit_count}",
        f"Surname Matches: {surname_hit_count}",
        f"Middle Name Matches: {middle_name_hit_count}",
        f"Extension Matches: {extension_hit_count}",
        f"Given + Surname Matches: {given_name_and_surname_hit_count}",
    ]

    if target_extension:
        stats_lines.append(f"Full Name (Without Extension): {name_without_extension_hit_count}")
    
    return "\n".join(stats_lines)


def main() -> None:
    run_name_generator(
        "feminine",
        amount=20,
        output_filename="output.csv",
        delay_in_seconds=0.01,
        include_email_and_password=True,
    )


if __name__ == "__main__":
    main()