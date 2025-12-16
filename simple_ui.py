#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox
import json

import uvm_asm_v28 as asm_module
import uvm_interp_v28 as interp_module

DEMO_PROGRAM = """load_const;0;100
load_const;1;75
write_value;0;10;0
write_value;1;10;1
load_const;20;100
greater_or_equal;20;0;0
greater_or_equal;20;1;1
"""


class UVMApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("УВМ - Вариант 28")
        self.window.geometry("800x600")

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.window, text="Программа УВМ (Вариант 28)",
                 font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.window, text="Программа (CSV формат):").pack(anchor="w", padx=20)
        self.input_text = scrolledtext.ScrolledText(self.window, height=10)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.input_text.insert("1.0", DEMO_PROGRAM)

        tk.Button(self.window, text="▶ Выполнить программу",
                  command=self.run_program, bg="green", fg="white",
                  font=("Arial", 12)).pack(pady=10)

        tk.Label(self.window, text="Результаты:").pack(anchor="w", padx=20)
        self.output_text = scrolledtext.ScrolledText(self.window, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.status_label = tk.Label(self.window, text="Готово", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def run_program(self):
        try:
            program_text = self.input_text.get("1.0", tk.END).strip()

            if not program_text:
                messagebox.showwarning("Ошибка", "Программа пуста!")
                return

            self.status_label.config(text="Ассемблирование...")
            self.window.update()

            bytecode, IR = asm_module.full_asm(program_text)

            self.status_label.config(text="Выполнение...")
            self.window.update()

            registers, memory = interp_module.execute(bytecode)

            result = {
                "status": "success",
                "commands_assembled": len(IR),
                "registers": {f"r{i}": val for i, val in enumerate(registers[:20]) if val != 0},
                "memory_sample": {i: memory[i] for i in range(min(50, len(memory))) if memory[i] != 0}
            }

            output = json.dumps(result, indent=2, ensure_ascii=False)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output)

            self.status_label.config(text=f"✅ Выполнено {len(IR)} команд")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_label.config(text=f"❌ Ошибка: {str(e)}")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = UVMApp()
    app.run()