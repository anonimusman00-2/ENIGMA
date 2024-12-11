# INSTALLATION

Install termux at https://f-droid.org/id/packages/com.termux/

-If you have installed F-droid immediately search for

-Termux
-Termux-API
-Termux:Widget
-Termux:Float
-Termux:Tasker

-Install all then install macrodroid at https://liteapks.com/macrodroid.html

-Then install

-open termux and type this at the beginning

```bash
apt update && apt upgrade -y

apt install python -y

apt install termux-api -y
```

termux-setup-storage

-After that create a .shortcuts folder in termux in the ~/.shortcuts section

Type the command

```bash
mkdir ~/.shortcuts
```

-after that move all the run.sh files and the Enigma.py files of your choice to ~/.shortcuts

-Type the command

```bash
mv /sdcard/downloads/EnigmaWT-EN.py ~/.shortcuts

mv /sdcard/downloads/run.sh ~/.shortcuts
```

-adjust the file location with original location and adjust the file that is run by typing

```bash
nano ~/.shortcuts/run.sh
```

-if it is saved

-edit the file name section you want

-then allow all files by typing

```bash
chmod +x ~/.shortcuts/*

chmod u+x ~/.shortcuts/*
```

-Then edit the termux section by typing

```bash
nano ~/.termux/*
```

-Then edit the section

```bash
#allow-external-apps = true
```

-Just delete the hashtag # and save

-After that open macrodroid and allow everything the application needs

-Create a new macro named Enigma with an empty trigger and select Action

Application >> Tasker Plugin / Local >> Termux:Tasker >> Termux

Settings like this

-Executable (file in...)

```bash
~/.shortcuts/run.sh
```

-Terminal Session Action

```bash
0
```

-Checklist Execute in a terminal session

-Checklist Wait for result for commands

-Save >> Ok

-Go back to the macro menu and long click Enigma >> Create Home Screen Shortcut >> Customize it yourself according to your needs

-Enigma is ready to run via shortcut

-You can send the encryption and decryption results via WhatsApp or Telegram



# التثبيت

قم بتثبيت تيرمكس من https://f-droid.org/id/packages/com.termux

-إذا قمت بتثبيت F-droid، ابحث مباشرة عن

-Termux
-Termux-API
-Termux:Widget
-Termux:Float
-Termux:Tasker

-قم بتثبيت كل هذه التطبيقات ثم قم بتثبيت ماكرودرويد من https://liteapks.com/macrodroid.html

-ثم قم بالتثبيت

-افتح تيرمكس واكتب هذا في البداية

```bash
apt update && apt upgrade -y

apt install python -y

apt install termux-api -y
```

termux-setup-storage

-بعد ذلك قم بإنشاء مجلد shortcuts. في تيرمكس في قسم ~/.shortcuts

اكتب الأمر

```bash
mkdir ~/.shortcuts
```

-بعد ذلك انقل جميع ملفات run.sh وملفات Enigma.py التي تختارها إلى ~/.shortcuts

-اكتب الأمر

```bash
mv /sdcard/downloads/EnigmaWT-EN.py ~/.shortcuts

mv /sdcard/downloads/run.sh ~/.shortcuts
```

-قم بتعديل موقع الملف مع الموقع الأصلي وقم بتعديل الملف الذي يتم تشغيله عن طريق كتابة

```bash
nano ~/.shortcuts/run.sh
```

-إذا تم حفظه

-قم بتعديل قسم اسم الملف الذي تريده

-ثم اسمح لجميع الملفات عن طريق كتابة

```bash
chmod +x ~/.shortcuts/*

chmod u+x ~/.shortcuts/*
```

-ثم قم بتحرير قسم تيرمكس عن طريق كتابة

```bash
nano ~/.termux/*
```

-ثم قم بتحرير القسم

```bash
#allow-external-apps = true
```

-فقط قم بحذف علامة الشباك # واحفظ

-بعد ذلك افتح ماكرودرويد واسمح بكل ما يحتاجه التطبيق

-قم بإنشاء ماكرو جديد باسم Enigma مع محفز فارغ واختر الإجراء

التطبيق >> Tasker Plugin / Local >> Termux:Tasker >> Termux

الإعدادات كالتالي

-الملف القابل للتنفيذ (الملف في...)

```bash
~/.shortcuts/run.sh
```

-إجراء جلسة الطرفية

```bash
0
```

-قائمة التحقق تنفيذ في جلسة طرفية

-قائمة التحقق انتظار النتيجة للأوامر

-حفظ >> موافق

-ارجع إلى قائمة الماكرو واضغط ضغطة طويلة على Enigma >> إنشاء اختصار على الشاشة الرئيسية >> قم بتخصيصه حسب احتياجاتك

-Enigma جاهز للتشغيل عبر الاختصار

-يمكنك إرسال نتائج التشفير وفك التشفير عبر واتساب أو تيليجرام
