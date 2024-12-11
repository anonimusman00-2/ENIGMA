import string  
import random  
import datetime  
import os  
import tkinter as tk  
from tkinter import ttk, scrolledtext, messagebox, filedialog  

# Constants  
ALL_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits  

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

    def get_position(self):  
        return self.position  

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
        self.plugboard_pairs = plugboard_pairs  
        if plugboard_pairs:  
            for a, b in plugboard_pairs:  
                if a in ALL_CHARS and b in ALL_CHARS:  
                    self.plugboard[a] = b  
                    self.plugboard[b] = a  
        
        self.reflector_pairs = reflector_pairs  
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
            
            # Format plugboard dan reflector  
            if plugboard_pairs:  
                f.write(f"Plugboard: {plugboard_pairs}\n")  
            else:  
                f.write("Plugboard: None\n")  
                
            if reflector_pairs:  
                f.write(f"Reflector: {reflector_pairs}\n")  
            else:  
                f.write("Reflector: None\n")  
        return True  
    except Exception as e:  
        print(f"\nError saving file: {e}")  
        return False  

class EnigmaGUI:  
    def __init__(self):  
        self.window = tk.Tk()  
        self.window.title("Enigma Ultra")  
        self.window.geometry("1000x800")  
        
        # Configuration variables  
        self.rotor_positions = []  
        self.plugboard_pairs = []  
        self.reflector_pairs = []  
        self.enigma = None  
        self.operation_mode = "encrypt"  
        
        self.create_gui()  
        
    def create_gui(self):  
        # Main container  
        main_frame = ttk.Frame(self.window, padding="10")  
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  
        
        # Mode selection  
        mode_frame = ttk.LabelFrame(main_frame, text="Operation Mode", padding="5")  
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)  
        
        self.mode_var = tk.StringVar(value="encrypt")  
        ttk.Radiobutton(mode_frame, text="Encrypt", variable=self.mode_var,   
                       value="encrypt", command=self.update_mode).grid(row=0, column=0, padx=5)  
        ttk.Radiobutton(mode_frame, text="Decrypt", variable=self.mode_var,  
                       value="decrypt", command=self.update_mode).grid(row=0, column=1, padx=5)  
        
        # Configuration frame  
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="5")  
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)  
        
        # Rotor positions  
        ttk.Label(config_frame, text="Rotor Positions (space-separated numbers):").grid(row=0, column=0, sticky=tk.W)  
        self.rotor_entry = ttk.Entry(config_frame, width=50)  
        self.rotor_entry.grid(row=0, column=1, padx=5, pady=2)  
        self.rotor_entry.insert(0, "1 2 3")  
        
        # Plugboard pairs  
        ttk.Label(config_frame, text="Plugboard Pairs (e.g., Ab Cd Ef):").grid(row=1, column=0, sticky=tk.W)  
        self.plugboard_entry = ttk.Entry(config_frame, width=50)  
        self.plugboard_entry.grid(row=1, column=1, padx=5, pady=2)  
        
        # Reflector pairs  
        ttk.Label(config_frame, text="Reflector Pairs (e.g., Xy Wz):").grid(row=2, column=0, sticky=tk.W)  
        self.reflector_entry = ttk.Entry(config_frame, width=50)  
        self.reflector_entry.grid(row=2, column=1, padx=5, pady=2)  
        
        # Apply configuration button  
        ttk.Button(config_frame, text="Apply Configuration",   
                  command=self.apply_configuration).grid(row=3, column=0, columnspan=2, pady=5)  
        
        # Text areas  
        text_frame = ttk.Frame(main_frame)  
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)  
        
        # Input text  
        input_frame = ttk.LabelFrame(text_frame, text="Input Text", padding="5")  
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)  
        self.input_text = scrolledtext.ScrolledText(input_frame, width=50, height=15)  
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  
        self.input_text.bind('<KeyRelease>', self.process_text)  
        
        # Output text  
        output_frame = ttk.LabelFrame(text_frame, text="Output Text", padding="5")  
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)  
        self.output_text = scrolledtext.ScrolledText(output_frame, width=50, height=15)  
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  
        
        # Buttons frame  
        button_frame = ttk.Frame(main_frame)  
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)  
        
        ttk.Button(button_frame, text="Clear", command=self.clear_text).grid(row=0, column=0, padx=5)  
        ttk.Button(button_frame, text="Save Result", command=self.save_result).grid(row=0, column=1, padx=5)  
        ttk.Button(button_frame, text="Generate Pairs", command=self.generate_pairs).grid(row=0, column=2, padx=5)  
        
        # Configure grid weights  
        main_frame.columnconfigure(0, weight=1)  
        text_frame.columnconfigure(0, weight=1)  
        text_frame.columnconfigure(1, weight=1)  
    
    def update_mode(self):  
        self.operation_mode = self.mode_var.get()  
        self.process_text(None)  
        
    def apply_configuration(self):  
        try:  
            # Parse rotor positions  
            positions = [int(x) for x in self.rotor_entry.get().strip().split()]  
            if not positions:  
                raise ValueError("Must have at least 1 rotor!")  
            
            # Parse plugboard and reflector pairs  
            plugboard_pairs = parse_pairs(self.plugboard_entry.get().strip())  
            reflector_pairs = parse_pairs(self.reflector_entry.get().strip())  
            
            # Create new Enigma machine  
            self.enigma = EnigmaMachine(positions, plugboard_pairs, reflector_pairs)  
            
            messagebox.showinfo("Success", "Configuration applied successfully!")  
            self.process_text(None)  # Update the output with new configuration  
            
        except Exception as e:  
            messagebox.showerror("Error", str(e))

    def process_text(self, event):  
        if not self.enigma:  
            try:  
                self.apply_configuration()  
            except:  
                return  
        
        input_text = self.input_text.get("1.0", tk.END).strip()  
        if input_text:  
            result = self.enigma.process_text(input_text)  
            
            # Update output text without triggering the event  
            self.output_text.delete("1.0", tk.END)  
            self.output_text.insert("1.0", result)  
    
    def clear_text(self):  
        self.input_text.delete("1.0", tk.END)  
        self.output_text.delete("1.0", tk.END)  
    
    def save_result(self):  
        try:  
            input_text = self.input_text.get("1.0", tk.END).strip()  
            output_text = self.output_text.get("1.0", tk.END).strip()  
            
            if not input_text or not output_text:  
                messagebox.showwarning("Warning", "No text to save!")  
                return  
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
            default_filename = f"enigma_{self.operation_mode}_{timestamp}.txt"  
            
            filename = filedialog.asksaveasfilename(  
                defaultextension=".txt",  
                initialfile=default_filename,  
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]  
            )  
            
            if filename:  
                # Ambil nilai plugboard dan reflector dari entry  
                plugboard = self.plugboard_entry.get().strip()  
                reflector = self.reflector_entry.get().strip()  
                
                save_to_file(  
                    filename,  
                    input_text,  
                    output_text,  
                    self.operation_mode,  
                    [int(x) for x in self.rotor_entry.get().strip().split()],  
                    plugboard,  
                    reflector  
                )  
                messagebox.showinfo("Success", f"Results saved to {filename}")  
            
        except Exception as e:  
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")  
    
    def generate_pairs(self):  
        plugboard_pairs, reflector_pairs = generate_plugboard_reflector()  
        self.plugboard_entry.delete(0, tk.END)  
        self.plugboard_entry.insert(0, format_pairs(plugboard_pairs))  
        self.reflector_entry.delete(0, tk.END)  
        self.reflector_entry.insert(0, format_pairs(reflector_pairs))  
        
    def run(self):  
        self.window.mainloop()  

def clear_screen():  
    if os.name == 'nt':  # For Windows  
        os.system('cls')  
    else:  # For macOS and Linux  
        os.system('clear')  

if __name__ == "__main__":  
    # Set window title  
    if os.name == 'nt':  # For Windows  
        os.system('title Enigma Ultra')  
    else:  # For Unix/Linux/Mac  
        print("\033]0;Enigma Ultra\007")  
        
    # Run the GUI application  
    app = EnigmaGUI()  
    app.run()