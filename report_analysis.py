
class Analysis:
    def __init__(self):
        self.text= """relays=0x000\ninputs=0x00\nM=0x5a04\nADC1=0.0 v\nADC2=0.0 v\nADC3=0.0 v\nADC4=0.0 v\nVdc=11.6 v
        \nVbat=0.0 v\nHUM=NC\nTEMP=-16.0\nHUM1=NC\nTEMP1=-15.9\nTEMP2=NC\nTEMP3=NC\nTEMP4=NC\nSIGNAL=26.0\nCredit=531.8
        \nUPTIME=123:39:31\nCloud=1,GSM\n9901=v5.3.0\n"""

    def Vbat(self):
        for line in self.text.splitlines():
            if line.startswith("Vbat="):
                vbat_value = float(line.split("=")[1].split()[0])  # مقدار عددی Vbat
                if vbat_value == 0.0:
                    return "ُبرق وصل بوده و وضعیت سالن مناسب است"
                else:
                    return "برق قطع است و سرخانه شما غیر فعال می باشد"

    def HUM1(self):
        for line in self.text.splitlines():
            if line.startswith("HUM1="):
                HUM1_value = line.split("=")[1].strip()  # مقدار HUM1 را جدا کنید
                if HUM1_value == 'NC':
                    return "سرخانه شما رطوبتی ندارد"
                else:
                    return f"رطوبت سرخانه شما {HUM1_value} درصد می باشد"


    def TEMP1(self):
        for line in self.text.splitlines():
            if line.startswith("TEMP1="):
                TEMP1_value = float(line.split("=")[1].strip())
                if TEMP1_value < 0:
                    return f"دمای سرخانه زیر صفر شما {TEMP1_value} درجه می باشد"
                else:
                    return f"دمای سرخانه زیر صفر شما افزایش یافته است و {TEMP1_value} درجه می باشد "

    def Credit(self):
        for line in self.text.splitlines():
            if line.startswith("Credit="):
                credit_value = float(line.split("=")[1].strip())
                return f"شارژ سرخانه شما {credit_value} ریال می باشد"

    def relays(self):
        for line in self.text.splitlines():
            if line.startswith("relays="):
                relays_value = line.split("=")[1].strip()
                if relays_value == '0x000':
                    return "همه دستگاه های سردخانه خاموش یا در حالت اتومات هستند"
                if relays_value == '0x001':
                    return "کمپرسور و سالن زیر صفر روشن هستند"
                if relays_value == '0x004':
                    return "سیستم در حال دیفراست و برفک زدایی می باشد"
                if relays_value == '0x008':
                    return "سالن بالای صفر روشن می باشد"
                if relays_value == '0x00f':
                    return "کلیه قسمت های زیر صفر و بالای صفر روشن و درحال کار می باشند"

    def inputs(self):
        for line in self.text.splitlines():
            if line.startswith("inputs="):
                inputs_value = line.split("=")[1].strip()
                if inputs_value == '0x01':
                    return "کنترل بار کمپرسور عمل کرده و سرخانه خاموش است"
                if inputs_value == '0x02':
                    return "سیستم با کمبود گاز مواجه شده و کمپرسور خاموش است"
                if inputs_value == '0x04':
                    return "حرارت بالای موتور باعث عملکرد ترمیستور حفاظتی شده و کمپرسور خاموش شده است"
                if inputs_value == '0x08':
                    return "برق ورودی سرخانه نقص دارد و باعث خاموش شدن سردخانه شده است لطفا برای رفع ایراد ورودی برق را چک کنید"
                if inputs_value == '0x08':
                    return "برق ورودی سرخانه نقص دارد و باعث خاموش شدن سردخانه شده است لطفا برای رفع ایراد ورودی برق را چک کنید"