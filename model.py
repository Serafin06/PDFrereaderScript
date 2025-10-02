import time
from pathlib import Path
from typing import Optional, Dict
import re, pdfplumber

from excelExtract import ExcelDataEnricher
from guiAutomator import MainWindowGUIAutomator
from interface import ITextExtractor, IDataParser, IDataEnricher, IGUIAutomator
from tempDataBase import PDFData


UNIT_MAP = {
    "Gramatur/Weight": r"g/m2",
    "OTR": r"cm3/m2 d at",
    "WVTR": r"g/m2d",
    "Grub./Thickness": r"μm"
}


class PDFTextExtractor(ITextExtractor):
    """Ekstrakcja tekstu z PDF"""

    def extract_text(self, file_path: Path) -> str:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)


class RegexDataParser(IDataParser):
    """Parsowanie danych z tekstu PDF"""

    def parse(self, text: str) -> PDFData:
        data = PDFData()


        # General Data
        data.card_no = self._extract(text, r"Card No\s*:\s*([^\n]+)")
        data.article_index = self._extract(text, r"Article index\s*:\s*([^\n]+)")
        data.client_article_index = self._extract(text, r"Client'?s?\s+article index\s*:\s*([^\n]+)")
        data.article_description = self._extract(text, r"Article description\s*:\s*([^\n]+)")
        data.product_structure = self._extract(text, r"Product structure\s*:\s*([^\n]+?)(?:\n|Structure)")
        data.structure_thickness = self._extract(text, r"Structure thickness\s*:\s*([^\n]+)")
        data.structure_description = self._extract(text, r"Structure description\s*:\s*([^\n]+?)(?:\n|Chemical)")
        data.chemical_composition = self._extract(text, r"Chemical composition\s*:\s*([^\n]+)")

        # Physico-chemical properties
        data.gramatura = self._extract_value(text, "Gramatur/Weight")
        data.otr = self._extract_value(text, "OTR")
        data.wvtr = self._extract_value(text, "WVTR")
        data.thickness = self._extract_value(text, "Grub./Thickness")

        # Print details
        data.print_type = self._extract(text, r"Print type\s*:\s*([^\n]+)")
        data.number_of_colours = self._extract(text, r"Number of colours\s*:\s*([^\n]+?)(?:\n|Solid)")
        data.solid_lacquer = self._extract(text, r"Solid/Lacquer\s*:\s*([^\n]+)")

        # Packing
        data.winding_code = self._extract(text, r"Winding code\s*:\s*([^\n]+?)(?:\n|Core)")
        data.core = self._extract(text, r"Core\s*:\s*([^\n]+)")
        data.external_diameter = self._extract(text, r"External diameter\s*:\s*([^\n]+?)(?:\n|Core)")
        data.width_of_core = self._extract(text, r"Width of core\s*:\s*([^\n]+)")
        data.core_submission = self._extract(text, r"Core submission\s*:\s*([^\n]+)")

        return data

    def _extract(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            result = match.group(1).strip()
            return re.sub(r'\s+', ' ', result)
        return ""

    def _extract_value(self, text: str, param_name: str) -> str:
        """
            Szuka wartości fizykochemicznej po nazwie parametru lub jednostce.
            Zwraca pierwszą liczbę po dopasowaniu jednostki.
            """
        unit_pattern = UNIT_MAP.get(param_name)
        if not unit_pattern:
            return None

        match = re.search(rf"{re.escape(unit_pattern)}\s+([\d,]+)", text)
        if match:
            return float(match.group(1).replace(",", "."))
        return None


# ============================================================================
# FACADE - Główny serwis
# ============================================================================

class PDFtoGUIService:
    """Facade: Automatyczny przepływ PDF → GUI → PDF"""

    def __init__(
            self,
            text_extractor: ITextExtractor,
            data_parser: IDataParser,
            data_enricher: IDataEnricher,
            gui_automator: IGUIAutomator
    ):
        self.text_extractor = text_extractor
        self.data_parser = data_parser
        self.data_enricher = data_enricher
        self.gui_automator = gui_automator

    def process_pdf(self, pdf_path: Path, prepared_by: str) -> bool:
        """
        Przetwarza PDF: wyciąga dane → wpisuje do GUI → generuje PDF

        Returns:
            bool: True jeśli sukces
        """
        try:
            print(f"\n{'=' * 70}")
            print(f"Przetwarzanie: {pdf_path.name}")
            print(f"{'=' * 70}")

            # 1. Ekstrakcja tekstu
            text = self.text_extractor.extract_text(pdf_path)
            print("  ✓ Wyekstrahowano tekst")

            # 2. Parsowanie danych
            data = self.data_parser.parse(text)
            data.prepared_by = prepared_by
            print("  ✓ Sparsowano dane")

            # 3. Wzbogacenie z Excel
            data = self.data_enricher.enrich(data, pdf_path.stem)

            # 4. Wypełnienie formularza GUI
            self.gui_automator.fill_form(data)

            # 5. Generowanie PDF
            self.gui_automator.generate_pdf()

            print(f"{'=' * 70}\n")
            return True

        except Exception as e:
            print(f"  ✗ BŁĄD: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_directory(self, directory: Path, prepared_by: str) -> Dict[str, int]:
        """Przetwarza wszystkie PDF-y z katalogu"""
        pdf_files = list(directory.glob("*.pdf"))

        if not pdf_files:
            print(f"⚠ Nie znaleziono plików PDF w: {directory}")
            return {'success': 0, 'failed': 0}

        print(f"\n📄 Znaleziono {len(pdf_files)} plików PDF\n")

        stats = {'success': 0, 'failed': 0}


        for pdf_file in pdf_files:
            if self.process_pdf(pdf_file, prepared_by):
                stats['success'] += 1
            else:
                stats['failed'] += 1

        print("\n⏳ Finalizacja...")


        return stats


# ============================================================================
# FACTORY
# ============================================================================

class PDFtoGUIServiceFactory:
    """Factory: Tworzenie serwisu z automatyzacją GUI"""

    @staticmethod
    def create(main_window, excel_path: Optional[Path] = None) -> PDFtoGUIService:
        """
        Args:
            main_window: Instancja MainWindow z Twojego programu
            excel_path: Opcjonalna ścieżka do Excel
        """
        text_extractor = PDFTextExtractor()
        data_parser = RegexDataParser()
        data_enricher = ExcelDataEnricher(excel_path)
        gui_automator = MainWindowGUIAutomator(main_window)

        return PDFtoGUIService(
            text_extractor=text_extractor,
            data_parser=data_parser,
            data_enricher=data_enricher,
            gui_automator=gui_automator
        )


