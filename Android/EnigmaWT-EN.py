import string  
import random  
import datetime  
import os  
import subprocess  
import time  
import urllib.parse  

# Set title for terminal  
if os.name == 'nt':  
    os.system('title Enigma Ultra')  
else:  
    print("\033]0;Enigma Ultra\007")  

# Define valid characters  
ALL_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits  

def clear_screen():  
    os.system('cls' if os.name == 'nt' else 'clear')  

def generate_pairs(characters):  
    shuffled = random.sample(characters, len(characters))  
    pairs = []  
    for i in range(0, len(shuffled), 2):  
        if i + 1 < len(shuffled):  
            pairs.append(shuffled[i] + shuffled[i+1])  
    return pairs  

def generate_plugboard_reflector():  
    characters = list(string.ascii_uppercase + string.ascii_lowercase + string.digits)  
    if len(characters) % 2 != 0:  
        characters = characters[:-1]  
    plugboard_pairs = generate_pairs(characters[:50])  
    reflector_pairs = generate_pairs(characters)  
    return plugboard_pairs, reflector_pairs  

def format_pairs(pairs):  
    return ' '.join(pairs)  

def get_message_input():  
    print("(Type your message and press Enter 6 times consecutively to finish. Max 5 Enter presses)")  
    message_lines = []  
    empty_count = 0  
    consecutive_empty = []  
    
    while empty_count < 5:  
        line = input()  
        if line.strip() == "":  
            empty_count += 1  
            consecutive_empty.append(line)  
        else:  
            if consecutive_empty:  
                message_lines.extend(consecutive_empty)  
                consecutive_empty = []  
            message_lines.append(line)  
            empty_count = 0  
    
    if len(consecutive_empty) > 1:  
        message_lines.extend(consecutive_empty[:-1])  
    
    return "\n".join(message_lines) 

class Rotor:  
    def __init__(self, seed):  
        self.size = len(ALL_CHARS)  
        self.position = 0  
        random.seed(seed)  
        self.forward_mapping = list(range(self.size))  
        random.shuffle(self.forward_mapping)  
        self.backward_mapping = [0] * self.size  
        for i in range(self.size):  
            self.backward_mapping[self.forward_mapping[i]] = i  
        self.notch = self.size // 2  

    def set_position(self, position):  
        self.position = position % self.size  

    def rotate(self):  
        self.position = (self.position + 1) % self.size  
        return self.position == self.notch  

    def transform(self, index, reverse=False):  
        shifted = (index + self.position) % self.size  
        mapping = self.backward_mapping if reverse else self.forward_mapping  
        result = mapping[shifted]  
        return (result - self.position) % self.size  

class Reflector:  
    def __init__(self, pairs=None):  
        self.size = len(ALL_CHARS)  
        self.mapping = list(range(self.size))  
        random.seed(42)  
        
        if pairs:  
            used = set()  
            for a, b in pairs:  
                if a in ALL_CHARS and b in ALL_CHARS:  
                    idx_a = ALL_CHARS.index(a)  
                    idx_b = ALL_CHARS.index(b)  
                    if idx_a not in used and idx_b not in used:  
                        self.mapping[idx_a] = idx_b  
                        self.mapping[idx_b] = idx_a  
                        used.add(idx_a)  
                        used.add(idx_b)  
        
        unpaired = [i for i in range(self.size) if self.mapping[i] == i]  
        for i in range(0, len(unpaired)-1, 2):  
            self.mapping[unpaired[i]] = unpaired[i+1]  
            self.mapping[unpaired[i+1]] = unpaired[i]  
            
        if len(unpaired) % 2:  
            self.mapping[unpaired[-1]] = unpaired[-1]  

    def reflect(self, index):  
        return self.mapping[index]  

class EnigmaMachine:  
    def __init__(self, rotor_positions, plugboard_pairs=None, reflector_pairs=None):  
        if not rotor_positions:  
            raise ValueError("Must have at least 1 rotor!")  
            
        self.initial_positions = rotor_positions.copy()  
        self.rotors = []  
        for i, pos in enumerate(rotor_positions):  
            rotor = Rotor(i + 1)  
            rotor.set_position(pos)  
            self.rotors.append(rotor)  
        
        self.plugboard = {}  
        if plugboard_pairs:  
            for a, b in plugboard_pairs:  
                if a in ALL_CHARS and b in ALL_CHARS:  
                    self.plugboard[a] = b  
                    self.plugboard[b] = a  
        
        self.reflector = Reflector(reflector_pairs)  

    def reset(self):  
        for rotor, pos in zip(self.rotors, self.initial_positions):  
            rotor.set_position(pos)  

    def transform_char(self, char):  
        if char not in ALL_CHARS:  
            return char  
            
        current = self.plugboard.get(char, char)  
        index = ALL_CHARS.index(current)  
        
        for rotor in self.rotors:  
            index = rotor.transform(index)  
        
        index = self.reflector.reflect(index)  
        
        for rotor in reversed(self.rotors):  
            index = rotor.transform(index, reverse=True)  
        
        result = ALL_CHARS[index]  
        return self.plugboard.get(result, result)  

    def process_text(self, text):  
        self.reset()  
        
        result = []  
        for i, char in enumerate(text):  
            if i > 0:  
                carry = True  
                for rotor in self.rotors:  
                    if carry:  
                        carry = rotor.rotate()  
                    else:  
                        break  
            result.append(self.transform_char(char))  
            
        return ''.join(result)  

def parse_pairs(pairs_str):  
    if not pairs_str.strip():  
        return []  
        
    pairs = []  
    used = set()  
    
    for item in pairs_str.split():  
        if len(item) == 2:  
            a, b = item[0], item[1]  
            if a not in used and b not in used:  
                pairs.append((a, b))  
                used.add(a)  
                used.add(b)  
                
    return pairs  

def save_to_file(filename, message, result, operation, positions, plugboard_pairs, reflector_pairs):  
    try:  
        with open(filename, 'w', encoding='utf-8') as f:  
            f.write(f"=== {operation.upper()} RESULTS ===\n\n")  
            f.write("ORIGINAL MESSAGE:\n")  
            f.write(message)  
            f.write(f"\n\n{operation.upper()} MESSAGE:\n")  
            f.write(result)  
            f.write("\n\nCONFIGURATION USED:\n")  
            f.write(f"Number of rotors: {len(positions)}\n")  
            f.write(f"Rotor positions: {' '.join(map(str, positions))}\n")  
            if plugboard_pairs:  
                f.write(f"Plugboard: {' '.join(''.join(pair) for pair in plugboard_pairs)}\n")  
            else:  
                f.write("Plugboard: (default)\n")  
            if reflector_pairs:  
                f.write(f"Reflector: {' '.join(''.join(pair) for pair in reflector_pairs)}\n")  
            else:  
                f.write("Reflector: (default)\n")  
        return True  
    except Exception as e:  
        print(f"\nError saving file: {e}")  
        return False  

def send_direct_message(text):  
    """  
    Function to directly share encrypted/decrypted message  
    """  
    try:  
        print("\nSelect sharing method:")  
        print("1. WhatsApp")  
        print("2. Telegram")  
        app_choice = input("\nChoice (1/2): ").strip()  
        
        encoded_text = urllib.parse.quote(text)  
        
        if app_choice == "1":  
            command = f'termux-open-url "whatsapp://send?text={encoded_text}"'  
            subprocess.run(command, shell=True)  
            print("\nOpening WhatsApp share screen...")  
            
        elif app_choice == "2":  
            command = f'termux-open-url "tg://msg?text={encoded_text}"'  
            subprocess.run(command, shell=True)  
            print("\nOpening Telegram share screen...")  
            
        else:  
            print("\nInvalid choice!")  
            return False  
            
        time.sleep(2)  
        return True  
        
    except Exception as e:  
        print(f"\nError sharing message: {e}")  
        return False  

def main():  
    while True:  
        print("\n=== ENIGMA ULTRA MACHINE ===")  
        print("1. Encrypt & Share Message")  
        print("2. Decrypt & Share Message")  
        print("3. Generate Plugboard and Reflector")  
        print("4. Clear Screen")  
        
        choice = input("\nSelect menu: ").strip()  
        
        if choice == '4':  
            clear_screen()  
            continue  
            
        elif choice in ['1', '2']:  
            try:  
                print("\nEnter rotor positions (numbers separated by spaces):")  
                positions = [int(x) for x in input("Rotor positions: ").strip().split()]  
                
                if not positions:  
                    raise ValueError("Must have at least 1 rotor!")  
                
                print("\nEnter Plugboard pairs (example: Ab 2y Cx):")  
                print("(leave empty if not needed)")  
                plugboard_pairs = parse_pairs(input("Plugboard: ").strip())  
                
                print("\nEnter Reflector pairs (example: Xy 9z 2N):")  
                print("(leave empty for default)")  
                reflector_pairs = parse_pairs(input("Reflector: ").strip())  
                
                enigma = EnigmaMachine(positions, plugboard_pairs, reflector_pairs)  
                
                print("\nEnter message to", "encrypt:" if choice == '1' else "decrypt:")  
                message = get_message_input()  
                
                result = enigma.process_text(message)  
                
                print("\nMessage", "Encrypted:" if choice == '1' else "Decrypted:")  
                print(result)  
                
                share_now = input("\nShare message now? (y/n): ").lower().strip()  
                
                if share_now == 'y':  
                    if send_direct_message(result):  
                        print("\nMessage ready to share!")  
                    else:  
                        print("\nFailed to open sharing options")  
                
                save_choice = input("\nSave results to file? (y/n): ").lower().strip()  
                
                if save_choice == 'y':  
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
                    operation = "encryption" if choice == '1' else "decryption"  
                    default_filename = f"{operation}_result_{timestamp}.txt"  
                    
                    print(f"\nDefault filename: {default_filename}")  
                    custom_filename = input("Enter custom filename (leave empty for default): ").strip()  
                    
                    filename = custom_filename if custom_filename else default_filename  
                    if not filename.endswith('.txt'):  
                        filename += '.txt'  
                    
                    if save_to_file(filename, message, result, operation, positions, plugboard_pairs, reflector_pairs):  
                        print(f"\n{operation.capitalize()} results saved to: {filename}")  
                
                print("\nConfiguration used:")  
                print(f"Number of rotors: {len(positions)}")  
                print("Rotor positions:", " ".join(map(str, positions)))  
                if plugboard_pairs:  
                    print("Plugboard:", " ".join("".join(pair) for pair in plugboard_pairs))  
                else:  
                    print("Plugboard: (default)")  
                if reflector_pairs:  
                    print("Reflector:", " ".join("".join(pair) for pair in reflector_pairs))  
                else:  
                    print("Reflector: (default)")  
                    
            except ValueError as e:  
                print(f"\nError: {e}")  
                continue  
                
        elif choice == '3':  
            plugboard_pairs, reflector_pairs = generate_plugboard_reflector()  
            print("\nPLUGBOARD:")  
            print(format_pairs(plugboard_pairs))  
            print("\nREFLECTOR:")  
            print(format_pairs(reflector_pairs))  
            
            save = input("\nSave to file? (y/n): ").lower()  
            if save == 'y':  
                try:  
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
                    default_filename = f"enigma_pairs_{timestamp}.txt"  
                    print(f"\nDefault filename: {default_filename}")  
                    custom_filename = input("Enter custom filename (leave empty for default): ").strip()  
                    
                    filename = custom_filename if custom_filename else default_filename  
                    if not filename.endswith('.txt'):  
                        filename += '.txt'  
                    
                    with open(filename, 'w') as f:  
                        f.write("PLUGBOARD:\n")  
                        f.write(format_pairs(plugboard_pairs))  
                        f.write("\n\nREFLECTOR:\n")  
                        f.write(format_pairs(reflector_pairs))  
                    print(f"\nSuccessfully saved to: {filename}")  
                except Exception as e:  
                    print(f"\nFailed to save: {e}")  
            
        else:  
            print("\nInvalid choice!")  

if __name__ == "__main__":  
    main()