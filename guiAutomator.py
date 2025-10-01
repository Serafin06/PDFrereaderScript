import time
from pathlib import Path

import pyautogui

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
        # Używamy nazw zgodnych z domyślną tabelą i dodajemy nowe jeśli potrzeba
        if data.gramatura:
            self._add_or_update_property(
                property_name="Weight",
                value=data.gramatura,
                method="PN-81/P 50129",
                unit="g/m²",
                deviation="-15 +15 %"
            )
        if data.otr:
            self._add_or_update_property(
                property_name="OTR (barrier O₂)",
                value=data.otr,
                method="DIN 53380",
                unit="cm³/m²×24h×0,1MPa",
                deviation="-1 +2 cm³/m²×24h×0,1MPa"
            )
        if data.wvtr:
            self._add_or_update_property(
                property_name="WVTR (barrier H₂O)",
                value=data.wvtr,
                method="DIN 53122",
                unit="g/m²×24h",
                deviation="-2 +3 g/m²×24h"
            )
        if data.thickness:
            self._add_or_update_property(
                property_name="Thickness",
                value=data.thickness,
                method="PN-ISO 4593",
                unit="μm",
                deviation="-10 +10 %"
            )

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
            combo = self.window.podpisy_frame.opracowal_combo
            combo.set(data.prepared_by)

    def _set_property_value(self, property_name: str, value: str) -> None:
        """Wpisuje wartość właściwości bezpośrednio w Treeview"""
        try:
            # Bezpośredni dostęp do Treeview
            for item in self.window.wlasciwosci_table.tree.get_children():
                values = self.window.wlasciwosci_table.tree.item(item, 'values')

                # values[0] = Lp.
                # values[1] = Parametr (nazwa właściwości)
                # values[2] = Metoda badania
                # values[3] = Wartość ← tutaj wpisujemy
                # values[4] = Jednostka
                # values[5] = Odchylenie

                if len(values) >= 6 and str(values[1]) == property_name:
                    # Zaktualizuj tylko wartość (indeks 3)
                    new_values = list(values)
                    new_values[3] = value
                    self.window.wlasciwosci_table.tree.item(item, values=new_values)
                    print(f"  ✓ Ustawiono {property_name} = {value}")
                    return

            print(f"  ⚠ Nie znaleziono właściwości: {property_name}")

        except Exception as e:
            print(f"  ⚠ Błąd przy ustawianiu {property_name}: {e}")

    def generate_pdf(self) -> None:
        """Generuje PDF klikając przycisk w GUI i automatycznie zatwierdza okna systemowe"""
        self.window._generate_pdf()  # kliknięcie "Generuj PDF"

        time.sleep(0.8)

        pyautogui.press("enter")

        # Odczekaj chwilę na wygenerowanie PDF i popup z informacją
        time.sleep(0.8)

        # Kliknij OK w popupie z informacją o wygenerowanym PDF
        pyautogui.press("enter")

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

    def _map_property_name(self, pdf_name: str) -> str:
        """Mapuje nazwy z PDF na nazwy w tabeli"""
        mapping = {
            "Gramatura": "Weight",
            "OTR (bariera O₂)": "OTR (barrier O₂)",
            "WVTR (bariera H₂O)": "WVTR (barrier H₂O)",
            "Grubość": "Thickness"  # Jeśli w tabeli jest "Thickness"
        }
        return mapping.get(pdf_name, pdf_name)

    def _add_or_update_property(self, property_name: str, value: str, method: str = "-", unit: str = "μm",
                                deviation: str = "- -") -> None:
        """
        Dodaje właściwość do tabeli lub aktualizuje jeśli istnieje

        Args:
            property_name: Nazwa parametru
            value: Wartość
            method: Metoda badania
            unit: Jednostka
            deviation: Odchylenie
        """
        try:
            # Najpierw sprawdź czy właściwość już istnieje
            found = False
            for item in self.window.wlasciwosci_table.tree.get_children():
                values = self.window.wlasciwosci_table.tree.item(item, 'values')

                if len(values) >= 6 and str(values[1]) == property_name:
                    # Zaktualizuj istniejącą właściwość
                    new_values = list(values)
                    new_values[3] = value  # Wartość
                    self.window.wlasciwosci_table.tree.item(item, values=new_values)
                    print(f"  ✓ Zaktualizowano {property_name} = {value}")
                    found = True
                    break

            # Jeśli nie znaleziono, dodaj nową właściwość
            if not found:
                lp = len(self.window.wlasciwosci_table.tree.get_children()) + 1
                new_values = [str(lp), property_name, method, value, unit, deviation]
                self.window.wlasciwosci_table.tree.insert("", "end", values=new_values)
                print(f"  ✓ Dodano {property_name} = {value}")

        except Exception as e:
            print(f"  ⚠ Błąd przy dodawaniu/aktualizacji {property_name}: {e}")

