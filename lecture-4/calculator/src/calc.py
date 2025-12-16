import flet as ft
import math

# --- Button Classes (変更なし) ---
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK

# --- New Scientific Button Class ---
class ScientificActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_400  # 科学計算用に異なる色を設定
        self.color = ft.Colors.WHITE
# -----------------------------------


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        
        # 度の代わりにラジアンを使用していることをユーザーに伝えるためのフラグ
        self.degrees_mode = False 

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 450 # 幅を広げ、科学計算ボタンに対応
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                # --- Scientific Buttons Row 1 ---
                ft.Row(
                    controls=[
                        ScientificActionButton(text="sin", button_clicked=self.button_clicked),
                        ScientificActionButton(text="cos", button_clicked=self.button_clicked),
                        ScientificActionButton(text="tan", button_clicked=self.button_clicked),
                        ScientificActionButton(text="ln", button_clicked=self.button_clicked),
                        ScientificActionButton(text="$e^x$", button_clicked=self.button_clicked),
                        ScientificActionButton(text="$x^2$", button_clicked=self.button_clicked),
                    ]
                ),
                # --- Basic Action Buttons Row ---
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        # print(f"Button clicked with data = {data}")
        
        # エラー表示中またはACボタンが押された場合
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
        
        # 数字と小数点の入力
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        # 二項演算子 (+, -, *, /)
        elif data in ("+", "-", "*", "/"):
            try:
                # 既存の演算を実行
                self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
                self.operator = data
                if self.result.value == "Error":
                    self.operand1 = 0
                else:
                    self.operand1 = float(self.result.value)
                self.new_operand = True
            except ValueError: # float変換エラーなど
                self.result.value = "Error"
                self.reset()
        
        # 科学計算モードの単項演算子 (sin, cos, tan, ln, $e^x$, $x^2$)
        elif data in ("sin", "cos", "tan", "ln", "$e^x$", "$x^2$"):
            try:
                current_value = float(self.result.value)
                self.result.value = self.scientific_calculate(current_value, data)
                self.new_operand = True
                self.operand1 = float(self.result.value) if self.result.value != "Error" else 0
            except ValueError:
                self.result.value = "Error"
                self.reset()

        # 等号 (=)
        elif data in ("="):
            try:
                self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
                self.reset()
            except ValueError:
                self.result.value = "Error"
                self.reset()

        # パーセント (%)
        elif data in ("%"):
            try:
                self.result.value = self.format_number(float(self.result.value) / 100)
                self.reset()
            except ValueError:
                self.result.value = "Error"
                self.reset()

        # プラス/マイナス (+/-)
        elif data in ("+/-"):
            try:
                current_value = float(self.result.value)
                if current_value > 0:
                    self.result.value = "-" + str(self.format_number(current_value))
                elif current_value < 0:
                    self.result.value = str(self.format_number(abs(current_value)))
            except ValueError:
                self.result.value = "Error"
                self.reset()
                
        self.update()

    def format_number(self, num):
        # 10桁以上の整数または小数点以下6桁以上の場合は、指数表記を避けるために丸める
        if abs(num) >= 1e10 or (abs(num) < 1e-6 and abs(num) > 0) or len(str(num).split('.')[-1]) > 8:
             # 計算機の表示に合わせて適度に丸める
             num = round(num, 10) 
             
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        # 以前のコードと二項演算のロジックは同じ

        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)
        
        # 初回など、operatorが「+」の場合にoperand1が0として加算されるのを防ぐ（リセット後の挙動）
        return self.format_number(operand2)


    # --- New Scientific Calculation Method ---
    def scientific_calculate(self, operand, operator):
        # Pythonのmathモジュールを使用

        if operator == "sin":
            # math.sinはラジアンを要求
            return self.format_number(math.sin(operand)) 

        elif operator == "cos":
            return self.format_number(math.cos(operand))

        elif operator == "tan":
            # 90度の奇数倍付近でエラーになる可能性を考慮
            if math.cos(operand) == 0:
                return "Error" 
            return self.format_number(math.tan(operand))

        elif operator == "ln":
            # 自然対数 (log base e)
            if operand <= 0:
                return "Error" # 0または負の数の対数は未定義
            return self.format_number(math.log(operand))

        elif operator == "$e^x$":
            # 自然対数の底eのx乗
            return self.format_number(math.exp(operand))
            
        elif operator == "$x^2$":
            # 二乗
            return self.format_number(operand * operand)
            
        return self.format_number(operand)


    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Simple Calculator (Scientific Mode Added)"
    calc = CalculatorApp()
    page.add(calc)


ft.app(target=main)