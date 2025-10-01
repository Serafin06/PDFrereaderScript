import tkinter as tk
from tkinter import filedialog, simpledialog
from pathlib import Path


from model import PDFtoGUIServiceFactory
from models import DOSTEPNE_OSOBY


# ============================================================================
# INTEGRACJA Z TWOIM PROGRAMEM
# ============================================================================


def integrateWithGUI(main_window):
    """
    Funkcja do integracji z Twoim programem.
    Wywołaj ją po stworzeniu MainWindow.

    Użycie w Twoim main.py:
        from main_window import MainWindow
        from pdf_extractor import integrate_with_gui

        root = tk.Tk()
        app = MainWindow(root)

        # Dodaj przycisk "Import z PDF"
        integrate_with_gui(app)

        root.mainloop()
    """


    def import_from_pdf():
        """Handler dla przycisku Import z PDF"""
        # Wybór folderu z PDF-ami
        pdf_folder = filedialog.askdirectory(title="Wybierz folder z plikami PDF")
        if not pdf_folder:
            return

        # Wybór folderu docelowego dla wygenerowanych PDF-ów - wystarczy zmienic lokalizacje i Win juz sam bedzie tu zapisywal
        output_folder = filedialog.askdirectory(title="Wybierz folder do zapisu wygenerowanych PDF")
        if not output_folder:
            return

        # Pytanie o nazwisko
        root = tk.Tk()
        root.withdraw()

        dialog = ListaOsobDialog(root, title="Import z PDF")
        prepared_by = dialog.result

        if prepared_by:
            print("Wybrano:", prepared_by)
        else:
            print("Nie wybrano osoby")

        root.destroy()

        # Opcjonalnie: Excel
        excel_path = None
        use_excel = tk.messagebox.askyesno(
            "Import z PDF",
            "Czy chcesz użyć pliku Excel z dodatkowymi danymi?"
        )
        if use_excel:
            excel_file = filedialog.askopenfilename(
                title="Wybierz plik Excel",
                filetypes=[("Excel", "*.xlsx *.xls")]
            )
            if excel_file:
                excel_path = Path(excel_file)

        # Tworzenie serwisu i przetwarzanie
        service = PDFtoGUIServiceFactory.create(main_window, excel_path)
        stats = service.process_directory(Path(pdf_folder), prepared_by, output_folder)

        # Podsumowanie
        tk.messagebox.showinfo(
            "Import zakończony",
            f"Przetworzono pliki PDF:\n\n"
            f"✓ Sukces: {stats['success']}\n"
            f"✗ Błędy: {stats['failed']}\n\n"
            f"PDF-y zostały wygenerowane!"
        )

    # Dodaj przycisk "Import z PDF" do GUI
    import_button = tk.Button(
        main_window.root,
        text="📥 Import z PDF",
        command=import_from_pdf,
        font=("Arial", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=10
    )
    import_button.pack(side="left", padx=5)

    print("✓ Dodano funkcję 'Import z PDF' do GUI")

class ListaOsobDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Wybierz osobę przygotowującą:").pack()

        self.var = tk.StringVar(value=DOSTEPNE_OSOBY[0])
        self.menu = tk.OptionMenu(master, self.var, *DOSTEPNE_OSOBY)
        self.menu.pack(padx=10, pady=10)
        self.menu.config(width=25)
        return self.menu

    def apply(self):
        self.result = self.var.get()


