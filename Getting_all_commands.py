FORMAT = "utf-8"

def retrieve_all_commands(text_file):
    commands = []
    try:
        with open(text_file, 'r') as file:
            for line in file:
                command = line.strip()  # Remove any leading/trailing whitespace
                if command:
                    commands.append(command)
    except FileNotFoundError:
        print(f"Error: The file '{text_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return commands