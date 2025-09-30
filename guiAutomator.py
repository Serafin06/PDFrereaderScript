
from interface import IGUIAutomator
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
        # Rodzaj nadruku - parsowanie na 3 pola (warstwa/typ/symetria)
        if data.print_type:
            self._parse_print_type(data.print_type)

        # Ilość kolorów
        if data.number_of_colours:
            self.window.nadruk_frame.ilosc_kolorow_spin.delete(0, 'end')
            self.window.nadruk_frame.ilosc_kolorow_spin.insert(0, data.number_of_colours)

        # Lakier
        if data.solid_lacquer:
            if "Lakier" in self.window.nadruk_frame.fields:
                self.window.nadruk_frame.fields["Lakier"].delete(0, 'end')
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

    def _parse_print_type(self, print_type: str) -> None:
        """
        Parsuje rodzaj nadruku na 3 pola: warstwa, typ, symetria
        Przykład: "sandwich printing/reverse/symmetrical"
        """
        try:
            # Rozdziel po "/"
            parts = [p.strip() for p in print_type.split('/')]

            # Warstwa (sandwich printing / superficial)
            if len(parts) > 0:
                warstwa = parts[0]
                if warstwa in ["sandwich printing", "superficial"]:
                    self.window.nadruk_frame.warstwa_combo.set(warstwa)

            # Typ (simple / reverse)
            if len(parts) > 1:
                typ = parts[1]
                if typ in ["simple", "reverse"]:
                    self.window.nadruk_frame.typ_combo.set(typ)

            # Symetria (symmetrical / asymmetrical)
            if len(parts) > 2:
                symetria = parts[2]
                if symetria in ["symmetrical", "asymmetrical"]:
                    self.window.nadruk_frame.symetria_combo.set(symetria)

            print(f"  ✓ Ustawiono rodzaj nadruku: {print_type}")

        except Exception as e:
            print(f"  ⚠ Nie udało się sparsować rodzaju nadruku: {e}")