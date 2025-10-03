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
            return

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

        root.destroy()

        # Tworzenie serwisu i przetwarzanie

        service = PDFtoGUIServiceFactory.create(main_window, excel_path)
        stats = service.process_directory(Path(pdf_folder), prepared_by)


        print("IMPORT ZAKOŃCZONY")
        print(f"✓ Sukces: {stats['success']}")
        print(f"✗ Błędy: {stats['failed']}")
        print(f"PDF-y zostały wygenerowane!")

        # Stwórz nowe okno na podsumowanie


        def summaryBox ():

            summaryRoot = tk.Tk()
            summaryRoot.withdraw()

            tk.messagebox.showinfo(
                "Import zakończony",
                f"Przetworzono pliki PDF:\n\n"
                f"✓ Sukces: {stats['success']}\n"
                f"✗ Błędy: {stats['failed']}\n\n"
                f"PDF-y zostały wygenerowane!"
            )

            print("okienko")

            summaryRoot.destroy()

        summaryBox()
        print("==Koniec==")
        summaryBox()
        summaryBox()

    def import_single_pdf():
        """Handler dla przycisku Import pojedynczego PDF - tylko wczytanie danych"""

        # Wybór pliku PDF
        pdf_file = filedialog.askopenfilename(
            title="Wybierz plik PDF do zaimportowania",
            filetypes=[("PDF", "*.pdf")]
        )
        if not pdf_file:
            return

        # Tworzenie serwisu (bez Excel, bez prepared_by)
        service = PDFtoGUIServiceFactory.create(main_window, excel_path=None)

        try:
            # Przetwórz pojedynczy PDF
            text = service.text_extractor.extract_text(Path(pdf_file))
            data = service.data_parser.parse(text)

            # Wypełnij formularz (BEZ generowania PDF)
            service.gui_automator.fill_form(data)

            print(f"✓ Dane z {Path(pdf_file).name} zostały wczytane do formularza")

            # Potwierdzenie
            confirm_root = tk.Tk()
            confirm_root.withdraw()

            tk.messagebox.showinfo(
                "Import zakończony",
                f"Dane z pliku:\n{Path(pdf_file).name}\n\nzostały wczytane do formularza!",
                parent=confirm_root
            )

            confirm_root.destroy()

        except Exception as e:
            print(f"✗ Błąd podczas importu: {e}")

            error_root = tk.Tk()
            error_root.withdraw()

            tk.messagebox.showerror(
                "Błąd importu",
                f"Nie udało się zaimportować danych:\n{e}",
                parent=error_root
            )

            error_root.destroy()


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

    # Przycisk Import pojedynczego PDF (NOWY)
    import_single_button = tk.Button(
        main_window.root,
        text="📄 Import PDF (1 plik)",
        command=import_single_pdf,
        font=("Arial", 10, "bold"),
        bg="#2196F3",  # Inny kolor - niebieski
        fg="white",
        padx=20,
        pady=10
    )
    import_single_button.pack(side="left", padx=5)


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


