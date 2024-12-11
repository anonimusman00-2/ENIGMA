import string  
import random  
import datetime  
import os  
import tkinter as tk  
from tkinter import ttk, scrolledtext, messagebox, filedialog  

# Constants - Menambahkan karakter Arab  
ARABIC_CHARS = 'ابتثجحخدذرزسشصضطظعغفقكلمنهوياأإآةىؤئء٠١٢٣٤٥٦٧٨٩'  
ALL_CHARS = ARABIC_CHARS + string.digits + ' '  

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
            raise ValueError("يجب أن يكون هناك روتور واحد على الأقل!")  
            
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
    characters = list(ARABIC_CHARS)  
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
            f.write(f"=== {operation.upper()} نتائج ===\n\n")  
            f.write("الرسالة الأصلية:\n")  
            f.write(message)  
            f.write(f"\n\nالرسالة {operation.upper()}:\n")  
            f.write(result)  
            f.write("\n\nالإعدادات المستخدمة:\n")  
            f.write(f"عدد الروتورات: {len(positions)}\n")  
            f.write(f"مواقع الروتور: {' '.join(map(str, positions))}\n")  
            
            if plugboard_pairs:  
                f.write(f"لوحة التوصيل: {plugboard_pairs}\n")  
            else:  
                f.write("لوحة التوصيل: لا يوجد\n")  
                
            if reflector_pairs:  
                f.write(f"العاكس: {reflector_pairs}\n")  
            else:  
                f.write("العاكس: لا يوجد\n")  
        return True  
    except Exception as e:  
        print(f"\nخطأ في حفظ الملف: {e}")  
        return False  

class EnigmaGUI:  
    def __init__(self):  
        self.window = tk.Tk()  
        self.window.title("إنيجما الترا - النسخة العربية")  
        self.window.geometry("1000x800")  
        
        # تهيئة الخط العربي  
        self.arabic_font = ('Arial', 12)  
        
        # متغيرات التكوين  
        self.rotor_positions = []  
        self.plugboard_pairs = []  
        self.reflector_pairs = []  
        self.enigma = None  
        self.operation_mode = "تشفير"  
        
        self.create_gui()  
        
    def create_gui(self):  
        # الإطار الرئيسي  
        main_frame = ttk.Frame(self.window, padding="10")  
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  
        
        # اختيار الوضع  
        mode_frame = ttk.LabelFrame(main_frame, text="وضع التشغيل", padding="5")  
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)  
        
        self.mode_var = tk.StringVar(value="تشفير")  
        ttk.Radiobutton(mode_frame, text="تشفير", variable=self.mode_var,   
                       value="تشفير", command=self.update_mode).grid(row=0, column=0, padx=5)  
        ttk.Radiobutton(mode_frame, text="فك التشفير", variable=self.mode_var,  
                       value="فك التشفير", command=self.update_mode).grid(row=0, column=1, padx=5)  
        
        # إطار التكوين  
        config_frame = ttk.LabelFrame(main_frame, text="الإعدادات", padding="5")  
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)  
        
        # مواقع الروتور  
        ttk.Label(config_frame, text="مواقع الروتور (أرقام مفصولة بمسافات):",   
                 font=self.arabic_font).grid(row=0, column=0, sticky=tk.W)  
        self.rotor_entry = ttk.Entry(config_frame, width=50, font=self.arabic_font)  
        self.rotor_entry.grid(row=0, column=1, padx=5, pady=2)  
        self.rotor_entry.insert(0, "1 2 3")  
        
        # أزواج لوحة التوصيل  
        ttk.Label(config_frame, text="أزواج لوحة التوصيل (مثال: اب تث جح):",   
                 font=self.arabic_font).grid(row=1, column=0, sticky=tk.W)  
        self.plugboard_entry = ttk.Entry(config_frame, width=50, font=self.arabic_font)  
        self.plugboard_entry.grid(row=1, column=1, padx=5, pady=2)  
        
        # أزواج العاكس  
        ttk.Label(config_frame, text="أزواج العاكس (مثال: عغ فق):",   
                 font=self.arabic_font).grid(row=2, column=0, sticky=tk.W)  
        self.reflector_entry = ttk.Entry(config_frame, width=50, font=self.arabic_font)  
        self.reflector_entry.grid(row=2, column=1, padx=5, pady=2)  
        
        # زر تطبيق الإعدادات  
        ttk.Button(config_frame, text="تطبيق الإعدادات",   
                  command=self.apply_configuration).grid(row=3, column=0, columnspan=2, pady=5)

        # مناطق النص  
        text_frame = ttk.Frame(main_frame)  
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)  
        
        # نص الإدخال  
        input_frame = ttk.LabelFrame(text_frame, text="النص المدخل", padding="5")  
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)  
        self.input_text = scrolledtext.ScrolledText(input_frame, width=50, height=15, font=self.arabic_font)  
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  
        self.input_text.bind('<KeyRelease>', self.process_text)  
        
        # نص الإخراج  
        output_frame = ttk.LabelFrame(text_frame, text="النص الناتج", padding="5")  
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)  
        self.output_text = scrolledtext.ScrolledText(output_frame, width=50, height=15, font=self.arabic_font)  
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  
        
        # إطار الأزرار  
        button_frame = ttk.Frame(main_frame)  
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)  
        
        ttk.Button(button_frame, text="مسح",   
                  command=self.clear_text).grid(row=0, column=0, padx=5)  
        ttk.Button(button_frame, text="حفظ النتيجة",   
                  command=self.save_result).grid(row=0, column=1, padx=5)  
        ttk.Button(button_frame, text="توليد الأزواج",   
                  command=self.generate_pairs).grid(row=0, column=2, padx=5)  
        
        # تكوين أوزان الشبكة  
        main_frame.columnconfigure(0, weight=1)  
        text_frame.columnconfigure(0, weight=1)  
        text_frame.columnconfigure(1, weight=1)  
    
    def update_mode(self):  
        self.operation_mode = self.mode_var.get()  
        self.process_text(None)  
        
    def apply_configuration(self):  
        try:  
            # تحليل مواقع الروتور  
            positions = [int(x) for x in self.rotor_entry.get().strip().split()]  
            if not positions:  
                raise ValueError("يجب إدخال موقع روتور واحد على الأقل!")  
            
            # تحليل أزواج لوحة التوصيل والعاكس  
            plugboard_pairs = parse_pairs(self.plugboard_entry.get().strip())  
            reflector_pairs = parse_pairs(self.reflector_entry.get().strip())  
            
            # إنشاء آلة إنيجما جديدة  
            self.enigma = EnigmaMachine(positions, plugboard_pairs, reflector_pairs)  
            
            messagebox.showinfo("نجاح", "تم تطبيق الإعدادات بنجاح!")  
            self.process_text(None)  
            
        except Exception as e:  
            messagebox.showerror("خطأ", str(e))  
    
    def process_text(self, event):  
        if not self.enigma:  
            try:  
                self.apply_configuration()  
            except:  
                return  
        
        input_text = self.input_text.get("1.0", tk.END).strip()  
        if input_text:  
            result = self.enigma.process_text(input_text)  
            
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
                messagebox.showwarning("تحذير", "لا يوجد نص للحفظ!")  
                return  
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
            default_filename = f"enigma_{self.operation_mode}_{timestamp}.txt"  
            
            filename = filedialog.asksaveasfilename(  
                defaultextension=".txt",  
                initialfile=default_filename,  
                filetypes=[("ملفات نصية", "*.txt"), ("كل الملفات", "*.*")]  
            )  
            
            if filename:  
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
                messagebox.showinfo("نجاح", f"تم حفظ النتائج في {filename}")  
            
        except Exception as e:  
            messagebox.showerror("خطأ", f"فشل حفظ الملف: {str(e)}")  
    
    def generate_pairs(self):  
        plugboard_pairs, reflector_pairs = generate_plugboard_reflector()  
        self.plugboard_entry.delete(0, tk.END)  
        self.plugboard_entry.insert(0, format_pairs(plugboard_pairs))  
        self.reflector_entry.delete(0, tk.END)  
        self.reflector_entry.insert(0, format_pairs(reflector_pairs))  
        
    def run(self):  
        self.window.mainloop()  

if __name__ == "__main__":  
    # تعيين عنوان النافذة  
    if os.name == 'nt':  # لنظام Windows  
        os.system('title إنيجما الترا - النسخة العربية')  
    else:  # لنظام Unix/Linux/Mac  
        print("\033]0;إنيجما الترا - النسخة العربية\007")  
        
    # تشغيل التطبيق  
    app = EnigmaGUI()  
    app.run()