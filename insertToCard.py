from interfaces import IGUIAutomator
from tempDataBase import PDFData


class MainWindowGUIAutomator(IGUIAutomator):
    """Automatyzacja GUI - wpisuje dane i generuje PDF"""

    def __init__(self, main_window):
        """
        Args:
            main_window: Instancja MainWindow z Twojego programu
        """
        self.window = main_window

    def fill_form(self, data: PDFData) -> None:
        """Wpisuje dane do formularza GUI"""

        # Najpierw czyścimy formularz (nowa karta)
        self.window._new_karta()

        # === ARTYKUŁ ===
        self.window.artykul_frame.fields["Nr karty"].insert(0, data.card_no)
        self.window.artykul_frame.fields["Artykuł indeks"].insert(0, data.article_index)
        self.window.artykul_frame.fields["Artykuł klienta"].insert(0, data.client_article_index)
        self.window.artykul_frame.fields["Artykuł nazwa"].insert(0, data.article_description)
        self.window.artykul_frame.fields["Artykuł struktura"].insert(0, data.product_structure)
        self.window.artykul_frame.fields["Grubość struktury"].insert(0, data.structure_thickness)
        self.window.artykul_frame.fields["Opis struktury"].insert(0, data.structure_description)
        self.window.artykul_frame.fields["Skład chemiczny"].insert(0, data.chemical_composition)

        # === WŁAŚCIWOŚCI FIZYKOCHEMICZNE ===
        # Znajdujemy właściwości w tabeli i wpisujemy wartości
        if data.gramatura:
            self._set_property_value("Gramatura", data.gramatura)
        if data.otr:
            self._set_property_value("OTR (bariera O₂)", data.otr)
        if data.wvtr:
            self._set_property_value("WVTR (bariera H₂O)", data.wvtr)
        if data.thickness:
            self._set_property_value("Grubość", data.thickness)

        # === NADRUK ===
        if data.print_type:
            self.window.nadruk_frame.fields["Rodzaj nadruku"].insert(0, data.print_type)
        if data.number_of_colours:
            self.window.nadruk_frame.fields["Ilość kolorów"].insert(0, data.number_of_colours)
        if data.solid_lacquer:
            self.window.nadruk_frame.fields["Lakier"].insert(0, data.solid_lacquer)

        # === PAKOWANIE ===
        if data.winding_code:
            self.window.pakowanie_frame.fields["Kod nawoju"].insert(0, data.winding_code)
        if data.external_diameter:
            self.window.pakowanie_frame.fields["Średnica nawoju"].insert(0, data.external_diameter)
        if data.width_of_core:
            self.window.pakowanie_frame.fields["Szerokość tulei"].insert(0, data.width_of_core)
        if data.core_submission:
            self.window.pakowanie_frame.fields["Wysunięcie tulei"].insert(0, data.core_submission)

        # === PODPISY ===
        if data.prepared_by:
            self.window.podpisy_frame.fields["opracowal"].delete(0, 'end')
            self.window.podpisy_frame.fields["opracowal"].insert(0, data.prepared_by)

        print("  ✓ Dane wpisane do formularza")

    def _set_property_value(self, property_name: str, value: str) -> None:
        """Wpisuje wartość właściwości w tabeli"""
        try:
            # Znajdujemy właściwość w tabeli i wpisujemy wartość
            properties = self.window.wlasciwosci_table.get_properties()
            for prop in properties:
                if prop.nazwa == property_name:
                    prop.wartosc = value
            self.window.wlasciwosci_table.set_properties(properties)
        except Exception as e:
            print(f"  ⚠ Nie udało się ustawić {property_name}: {e}")

    def generate_pdf(self) -> None:
        """Generuje PDF klikając przycisk w GUI"""
        self.window._generate_pdf()
        print("  ✓ PDF wygenerowany")

# ============================================================================
# INTEGRACJA Z TWOIM PROGRAMEM
# ============================================================================


def integrate_with_gui(main_window):
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
    import tkinter as tk
    from tkinter import filedialog, simpledialog
    from pathlib import Path

    def import_from_pdf():
        """Handler dla przycisku Import z PDF"""
        # Wybór folderu z PDF-ami
        pdf_folder = filedialog.askdirectory(title="Wybierz folder z plikami PDF")
        if not pdf_folder:
            return

        # Pytanie o nazwisko
        prepared_by = simpledialog.askstring(
            "Import z PDF",
            "Podaj imię i nazwisko osoby przygotowującej:",
            initialvalue="Twoje Imię Nazwisko"
        )
        if not prepared_by:
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

        # Tworzenie serwisu i przetwarzanie
        service = PDFtoGUIServiceFactory.create(main_window, excel_path)
        stats = service.process_directory(Path(pdf_folder), prepared_by)

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