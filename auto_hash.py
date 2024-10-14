import hashid
import os
import subprocess
import random
from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
init(autoreset=True)

# Function to read and display the banner from a file
def display_banner():
    banner_file = 'banner.txt'  # Path to the banner text file
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    
    try:
        with open(banner_file, 'r') as file:
            banner = file.read()
        
        # Pick a random color each time the script runs
        color = random.choice(colors)
        print(color + banner)
    except FileNotFoundError:
        print(Fore.RED + "Banner file not found.")

# Function to read the hash from a file
def read_hash_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            hash_value = file.readline().strip()  # Read the first line as the hash
        print(f"Hash found in file: {hash_value}")
        return hash_value
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

# Function to identify the hash type
def identify_hash(hash_value):
    h = hashid.HashID()
    results = list(h.identifyHash(hash_value))  # Convert the generator to a list
    
    if results:
        print("\nIdentified Hash Types:")
        for result in results:
            print(f"Possible hash: {result.name}, Hashcat Mode: {result.hashcat}")
        
        # Filter results to only return the first valid Hashcat mode (i.e., where mode is not None)
        valid_modes = [result.hashcat for result in results if result.hashcat is not None]
        
        if valid_modes:
            return valid_modes[0]  # Return the first valid Hashcat mode
        else:
            print("No valid Hashcat mode found.")
            return None
    else:
        print("Hash type not identified.")
        return None



# Function to select the attack mode
def select_attack_mode():
    print("\nSelect the attack mode you want to use:")
    attack_modes = {
        "0": "Straight (Wordlist-based attack)",
        "1": "Combination",
        "3": "Brute-force",
        "6": "Hybrid Wordlist + Mask",
        "7": "Hybrid Mask + Wordlist"
    }

    for mode, description in attack_modes.items():
        print(f"{mode}: {description}")

    attack_mode = input("\nEnter the attack mode number: ")

    if attack_mode in attack_modes:
        return attack_mode
    else:
        print("Invalid attack mode selected.")
        return None

# Function to select character sets for brute-force or hybrid attacks
def select_character_sets():
    print("\nSelect the character sets you want to use:")
    char_sets = {
        "?l": "Lowercase letters (a-z)",
        "?u": "Uppercase letters (A-Z)",
        "?d": "Digits (0-9)",
        "?s": "Special characters (@, #, $, etc.)",
        "?a": "All printable ASCII characters",
        "?b": "All possible 8-bit byte values"
    }

    for char_set, description in char_sets.items():
        print(f"{char_set}: {description}")

    selected_sets = input("\nEnter the character sets you want to use (e.g., ?l?d for lowercase + digits): ")

    return selected_sets

# Function to list available rule files and select one
def select_rule_file():
    rules_directory = input("Enter the path to your Hashcat rules directory: ")  # Example: /usr/share/hashcat/rules
    try:
        rule_files = [f for f in os.listdir(rules_directory) if f.endswith('.rule')]
        if not rule_files:
            print("No rule files found in the specified directory.")
            return None

        print("\nAvailable rule files:")
        for i, rule_file in enumerate(rule_files):
            print(f"{i}: {rule_file}")

        selected_rule_index = int(input("\nEnter the number corresponding to the rule file you want to use: "))
        if 0 <= selected_rule_index < len(rule_files):
            return os.path.join(rules_directory, rule_files[selected_rule_index])
        else:
            print("Invalid selection.")
            return None
    except FileNotFoundError:
        print(f"Directory not found: {rules_directory}")
        return None
    except Exception as e:
        print(f"An error occurred while listing rule files: {e}")
        return None

# Function to prompt for the wordlist and rule files (for relevant attack modes)
def prompt_for_wordlist_and_rule():
    wordlist_path = input("Enter the path to your wordlist: ")
    use_rules = input("Do you want to apply a rule file? (yes/no): ").strip().lower()
    
    if use_rules == "yes":
        rule_path = select_rule_file()
        return wordlist_path, rule_path
    else:
        return wordlist_path, None

# Function to run the hashcat command
def crack_hash(hash_value, hashcat_mode, attack_mode, wordlist_path=None, rule_path=None, char_sets=None):
    if attack_mode == "3":  # Brute-force attack
        command = [
            "hashcat", "-m", str(hashcat_mode), "-a", str(attack_mode), hash_value, char_sets
        ]
    elif attack_mode in ["6", "7"]:  # Hybrid attacks
        command = [
            "hashcat", "-m", str(hashcat_mode), "-a", str(attack_mode), hash_value, wordlist_path, char_sets
        ]
    else:  # Wordlist-based or combination attack
        if rule_path:
            command = [
                "hashcat", "-m", str(hashcat_mode), "-a", str(attack_mode), hash_value, wordlist_path, "-r", rule_path
            ]
        else:
            command = [
                "hashcat", "-m", str(hashcat_mode), "-a", str(attack_mode), hash_value, wordlist_path
            ]

    print(f"\nRunning command: {' '.join(command)}")
    subprocess.run(command)

# Main function
def main():
    # Display the banner at the top of the script
    display_banner()

    file_path = input("Enter the path to the file containing the hash: ")

    # Read the hash from the file
    hash_value = read_hash_from_file(file_path)
    if hash_value is None:
        return

    # Identify the hash type and get the hashcat mode
    hashcat_mode = identify_hash(hash_value)
    if hashcat_mode is None:
        return

    # Let the user select the attack mode
    attack_mode = select_attack_mode()
    if attack_mode is None:
        return

    # Handle wordlist input for modes that require it
    if attack_mode in ["0", "1", "6"]:
        wordlist_path, rule_path = prompt_for_wordlist_and_rule()
        crack_hash(hash_value, hashcat_mode, attack_mode, wordlist_path, rule_path)
    # If brute-force or hybrid attack, ask for character sets
    elif attack_mode in ["3", "7"]:
        char_sets = select_character_sets()
        crack_hash(hash_value, hashcat_mode, attack_mode, char_sets=char_sets)
    else:
        print("Invalid mode or configuration.")

if __name__ == "__main__":
    main()
