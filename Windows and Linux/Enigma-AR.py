import string  
import random  
import datetime  
import os  

# Konfigurasi judul window  
if os.name == 'nt':  # For Windows  
    os.system('title جهاز إنيجما الترا')  
else:  # For Unix/Linux/Mac  
    print("\033]0;جهاز إنيجما الترا\007")  

# Karakter valid: huruf Arab dan angka Arab  
ALL_CHARS = 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي١٢٣٤٥٦٧٨٩٠'  

def clear_screen():  
    if os.name == 'nt':  
        os.system('cls')  
    else:  
        os.system('clear')  

def generate_pairs(characters):  
    shuffled = random.sample(characters, len(characters))  
    pairs = []  
    for i in range(0, len(shuffled), 2):  
        if i + 1 < len(shuffled):  
            pairs.append(shuffled[i] + shuffled[i+1])  
    return pairs  

def generate_plugboard_reflector():  
    characters = list(ALL_CHARS)  
    if len(characters) % 2 != 0:  
        characters = characters[:-1]  
    plugboard_pairs = generate_pairs(characters[:50])  
    reflector_pairs = generate_pairs(characters)  
    return plugboard_pairs, reflector_pairs  

def format_pairs(pairs):  
    return ' '.join(pairs)  

def get_message_input():  
    print("(اكتب الرسالة واضغط Enter 6 مرات متتالية للانتهاء، الحد الأقصى 5 مرات)")  
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
            raise ValueError("يجب أن يكون هناك دوار واحد على الأقل!")  
            
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
            f.write(f"=== نتائج {operation} ===\n\n")  
            f.write("الرسالة الأصلية:\n")  
            f.write(message)  
            f.write(f"\n\nالرسالة {operation}:\n")  
            f.write(result)  
            f.write("\n\nالإعدادات المستخدمة:\n")  
            f.write(f"عدد الدوارات: {len(positions)}\n")  
            f.write(f"مواضع الدوار: {' '.join(map(str, positions))}\n")  
            if plugboard_pairs:  
                f.write(f"لوحة التوصيل: {' '.join(''.join(pair) for pair in plugboard_pairs)}\n")  
            else:  
                f.write("لوحة التوصيل: (افتراضي)\n")  
            if reflector_pairs:  
                f.write(f"العاكس: {' '.join(''.join(pair) for pair in reflector_pairs)}\n")  
            else:  
                f.write("العاكس: (افتراضي)\n")  
        return True  
    except Exception as e:  
        print(f"\nخطأ في حفظ الملف: {e}")  
        return False  

def main():  
    while True:  
        print("\n=== جهاز إنيجما الترا ===")  
        print("١. تشفير الرسالة")  
        print("٢. فك تشفير الرسالة")  
        print("٣. إنشاء لوحة التوصيل والعاكس")  
        print("٤. مسح الشاشة")  
        
        choice = input("\nاختر القائمة: ").strip()  
        
        if choice == '٤':  
            clear_screen()  
            continue  
            
        elif choice == '٣':  
            plugboard_pairs, reflector_pairs = generate_plugboard_reflector()  
            print("\nلوحة التوصيل:")  
            print(format_pairs(plugboard_pairs))  
            print("\nالعاكس:")  
            print(format_pairs(reflector_pairs))  
            
            save = input("\nهل تريد حفظ النتائج في ملف؟ (ن/ي): ").lower()  
            if save == 'ي':  
                try:  
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
                    default_filename = f"enigma_pairs_{timestamp}.txt"  
                    print(f"\nاسم الملف الافتراضي: {default_filename}")  
                    custom_filename = input("أدخل اسم ملف مخصص (اتركه فارغًا لاستخدام الاسم الافتراضي): ").strip()  
                    
                    filename = custom_filename if custom_filename else default_filename  
                    if not filename.endswith('.txt'):  
                        filename += '.txt'  
                    
                    with open(filename, 'w', encoding='utf-8') as f:  
                        f.write("لوحة التوصيل:\n")  
                        f.write(format_pairs(plugboard_pairs))  
                        f.write("\n\nالعاكس:\n")  
                        f.write(format_pairs(reflector_pairs))  
                    print(f"\nتم الحفظ بنجاح في الملف: {filename}")  
                except Exception as e:  
                    print(f"\nفشل في حفظ الملف: {e}")  
            
        elif choice in ['١', '٢']:  
            try:  
                print("\nأدخل مواضع الدوار (أرقام) مفصولة بمسافات:")  
                positions = [int(x) for x in input("مواضع الدوار: ").strip().split()]  
                
                if not positions:  
                    raise ValueError("يجب أن يكون هناك دوار واحد على الأقل!")  
                
                print("\nأدخل أزواج لوحة التوصيل (مثال: اب تن حخ):")  
                print("(اتركه فارغًا إذا كنت لا تريد استخدام لوحة التوصيل)")  
                plugboard_pairs = parse_pairs(input("لوحة التوصيل: ").strip())  
                
                print("\nأدخل أزواج العاكس (مثال: طظ عغ كل):")  
                print("(اتركه فارغًا للعاكس الافتراضي)")  
                reflector_pairs = parse_pairs(input("العاكس: ").strip())  
                
                enigma = EnigmaMachine(positions, plugboard_pairs, reflector_pairs)  
                
                print("\nأدخل الرسالة المراد", "تشفيرها:" if choice == '١' else "فك تشفيرها:")  
                message = get_message_input()  
                
                result = enigma.process_text(message)  
                
                print("\nالرسالة", "المشفرة:" if choice == '١' else "بعد فك التشفير:")  
                print(result)  
                
                save_choice = input("\nهل تريد حفظ النتائج في ملف؟ (ن/ي): ").lower().strip()  
                
                if save_choice == 'ي':  
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
                    operation = "تشفير" if choice == '١' else "فك_تشفير"  
                    default_filename = f"نتائج_{operation}_{timestamp}.txt"  
                    
                    print(f"\nاسم الملف الافتراضي: {default_filename}")  
                    custom_filename = input("أدخل اسم ملف مخصص (اتركه فارغًا لاستخدام الاسم الافتراضي): ").strip()  
                    
                    filename = custom_filename if custom_filename else default_filename  
                    if not filename.endswith('.txt'):  
                        filename += '.txt'  
                    
                    if save_to_file(filename, message, result, operation, positions, plugboard_pairs, reflector_pairs):  
                        print(f"\nتم حفظ نتائج {operation} في الملف: {filename}")  
                
                print("\nالإعدادات المستخدمة:")  
                print(f"عدد الدوارات: {len(positions)}")  
                print("مواضع الدوار:", " ".join(map(str, positions)))  
                if plugboard_pairs:  
                    print("لوحة التوصيل:", " ".join("".join(pair) for pair in plugboard_pairs))  
                else:  
                    print("لوحة التوصيل: (افتراضي)")  
                if reflector_pairs:  
                    print("العاكس:", " ".join("".join(pair) for pair in reflector_pairs))  
                else:  
                    print("العاكس: (افتراضي)")  
                    
            except ValueError as e:  
                print(f"\nخطأ: {e}")  
                continue  
            
        else:  
            print("\nاختيار غير صالح!")  

if __name__ == "__main__":  
    main()