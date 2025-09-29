import datetime
import re
from dataclasses import asdict
from pathlib import Path
from turtle import pd
from typing import Optional, Dict, Any

from tempDataBase import ProductSpecification


class PDFSpecificationExtractor:
    def __init__(self, pdf_folder: str, excel_file: Optional[str] = None, output_folder: str = "output"):
        """
        Inicjalizacja ekstraktora specyfikacji z PDF

        Args:
            pdf_folder: folder z plikami PDF
            excel_file: ścieżka do pliku Excel z dodatkowymi parametrami
            output_folder: folder na wyniki
        """
        self.pdf_folder = Path(pdf_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        # Załaduj dane z Excela jeśli podano
        self.excel_data = None
        if excel_file and Path(excel_file).exists():
            self.excel_data = pd.read_excel(excel_file)
            print(f"Załadowano dane z Excel: {len(self.excel_data)} rekordów")

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Wyciąga cały tekst z PDF"""
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        return full_text

    def extract_value_from_pattern(self, text: str, pattern: str, group: int = 1) -> str:
        """Wyciąga wartość na podstawie wzorca regex"""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(group).strip() if match else ""

    def extract_table_row(self, text: str, row_name: str) -> Dict[str, str]:
        """
        Wyciąga dane z wiersza tabeli parametrów fizykochemicznych
        Format: Nazwa | Metoda | Jednostka | Wartość | -/+ | -/+ | Jednostka
        """
        # Szukamy linii z nazwą parametru
        pattern = rf"{row_name}.*?(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s+([^\n\r]+?)(?:\n|\r|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            value = match.group(1).strip()
            minus = match.group(2).strip()
            plus = match.group(3).strip()
            unit = match.group(4).strip()

            return {
                "value": value,
                "minus": minus,
                "plus": plus,
                "unit": unit
            }
        return {"value": "", "minus": "", "plus": "", "unit": ""}

    def extract_specification(self, pdf_path: Path) -> ProductSpecification:
        """Wyciąga kompletną specyfikację z pliku PDF"""
        spec = ProductSpecification()
        spec.source_file = pdf_path.stem
        spec.date = datetime.now().strftime("%Y-%m-%d")
        spec.prepared_by = "Twoje Imię"  # Zmień na swoje dane

        text = self.extract_text_from_pdf(pdf_path)

        # === 1. GENERAL DATA ===
        spec.card_no = self.extract_value_from_pattern(text, r"Card No\s*:\s*(.+?)(?:\n|Date)")
        spec.article_index = self.extract_value_from_pattern(text, r"Article index\s*:\s*(.+?)(?:\n|Client)")
        spec.client_article_index = self.extract_value_from_pattern(text,
                                                                    r"Client'?s?\s+article index\s*:\s*(.+?)(?:\n|Article description)")
        spec.article_description = self.extract_value_from_pattern(text,
                                                                   r"Article description\s*:\s*(.+?)(?:\n|Product structure)")
        spec.product_structure = self.extract_value_from_pattern(text,
                                                                 r"Product structure\s*:\s*(.+?)(?:\n|Structure description)")
        spec.structure_thickness = self.extract_value_from_pattern(text, r"Structure thickness\s*:\s*(.+?)(?:\n|Date)")
        spec.structure_description = self.extract_value_from_pattern(text,
                                                                     r"Structure description\s*:\s*(.+?)(?:\n|Chemical)")
        spec.chemical_composition = self.extract_value_from_pattern(text,
                                                                    r"Chemical composition\s*:\s*(.+?)(?:\n|Client)")

        # === 2. PHYSICO-CHEMICAL PROPERTIES ===
        # Gramatura
        gram_data = self.extract_table_row(text, r"Gramatur/Weight")
        spec.gramatura_value = gram_data["value"]
        spec.gramatura_minus = gram_data["minus"]
        spec.gramatura_plus = gram_data["plus"]
        spec.gramatura_unit = gram_data["unit"]

        # OTR
        otr_data = self.extract_table_row(text, r"OTR")
        spec.otr_value = otr_data["value"]
        spec.otr_minus = otr_data["minus"]
        spec.otr_plus = otr_data["plus"]
        spec.otr_unit = otr_data["unit"]

        # WVTR
        wvtr_data = self.extract_table_row(text, r"WVTR")
        spec.wvtr_value = wvtr_data["value"]
        spec.wvtr_minus = wvtr_data["minus"]
        spec.wvtr_plus = wvtr_data["plus"]
        spec.wvtr_unit = wvtr_data["unit"]

        # Grubość
        thick_data = self.extract_table_row(text, r"Grub\./Thickness")
        spec.thickness_value = thick_data["value"]
        spec.thickness_minus = thick_data["minus"]
        spec.thickness_plus = thick_data["plus"]
        spec.thickness_unit = thick_data["unit"]

        # === 3. PRINT DETAILS ===
        spec.print_type = self.extract_value_from_pattern(text, r"Print type\s*:\s*(.+?)(?:\n|Number)")
        spec.number_of_colours = self.extract_value_from_pattern(text, r"Number of colours\s*:\s*(.+?)(?:\n|Print)")
        spec.solid_lacquer = self.extract_value_from_pattern(text, r"Solid/Lacquer\s*:\s*(.+?)(?:\n|\d)")

        # === 4. PACKING ===
        spec.winding_code = self.extract_value_from_pattern(text, r"Winding code\s*:\s*(.+?)(?:\n|Reel)")
        spec.external_diameter = self.extract_value_from_pattern(text, r"External diameter\s*:\s*(.+?)(?:\n|Reels)")
        spec.width_of_core = self.extract_value_from_pattern(text, r"Width of core\s*:\s*(.+?)(?:\n|Core submission)")
        spec.core_submission = self.extract_value_from_pattern(text, r"Core submission\s*:\s*(.+?)(?:\n|Palette)")

        return spec

    def get_excel_data_for_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Pobiera dane z Excela dla danego pliku (na podstawie nazwy)"""
        if self.excel_data is None:
            return None

        # Szukamy wiersza w Excel pasującego do nazwy pliku
        # Zakładam, że w Excel jest kolumna z nazwą pliku lub article_index
        matching_rows = self.excel_data[
            (self.excel_data.astype(str).apply(lambda row: filename in row.values, axis=1))
        ]

        if not matching_rows.empty:
            return matching_rows.iloc[0].to_dict()
        return None

    def process_all_pdfs(self) -> pd.DataFrame:
        """Przetwarza wszystkie pliki PDF w folderze"""
        pdf_files = list(self.pdf_folder.glob("*.pdf"))

        if not pdf_files:
            print(f"Nie znaleziono plików PDF w: {self.pdf_folder}")
            return pd.DataFrame()

        print(f"Znaleziono {len(pdf_files)} plików PDF\n")

        all_specs = []

        for pdf_file in pdf_files:
            print(f"Przetwarzanie: {pdf_file.name}")

            try:
                # Wyciągnij specyfikację
                spec = self.extract_specification(pdf_file)

                # Dodaj dane z Excela jeśli dostępne
                excel_data = self.get_excel_data_for_file(pdf_file.stem)
                if excel_data:
                    print(f"  ✓ Znaleziono dane w Excel")
                    # Tutaj możesz nadpisać/uzupełnić dane z Excela
                    # spec.some_field = excel_data.get('column_name', spec.some_field)

                all_specs.append(asdict(spec))
                print(f"  ✓ Wyekstrahowano specyfikację")

            except Exception as e:
                print(f"  ✗ Błąd: {e}")
                continue

        return pd.DataFrame(all_specs)

    def save_results(self, df: pd.DataFrame, format: str = "all"):
        """
        Zapisuje wyniki w różnych formatach

        Args:
            df: DataFrame z wynikami
            format: 'csv', 'excel', 'json' lub 'all'
        """
        if df.empty:
            print("Brak danych do zapisania")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format in ["csv", "all"]:
            csv_path = self.output_folder / f"specifications_{timestamp}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"✓ Zapisano CSV: {csv_path}")

        if format in ["excel", "all"]:
            excel_path = self.output_folder / f"specifications_{timestamp}.xlsx"
            df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"✓ Zapisano Excel: {excel_path}")

        if format in ["json", "all"]:
            json_path = self.output_folder / f"specifications_{timestamp}.json"
            df.to_json(json_path, orient='records', indent=2, force_ascii=False)
            print(f"✓ Zapisano JSON: {json_path}")