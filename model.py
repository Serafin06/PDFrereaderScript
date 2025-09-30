import re
from pathlib import Path
from typing import Optional

import pdfplumber

from excelExtract import ExcelDataEnricher
from insertToCard import MinimalKartaMapper
from interfaces import ITextExtractor
from tempDataBase import ExtractedPDFData


class PDFTextExtractor(ITextExtractor):
    """Single Responsibility: Ekstrakcja tekstu z PDF"""

    def extract_text(self, file_path: Path) -> str:
        """Wyciąga cały tekst z pliku PDF"""
        text_parts = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts)


class RegexDataParser(IDataParser):
    """Single Responsibility: Parsowanie tekstu za pomocą regex"""

    def parse(self, text: str, file_name: str) -> ExtractedPDFData:
        """Parsuje tekst PDF - wyciąga TYLKO te dane, które są w PDF"""
        data = ExtractedPDFData(source_file=file_name)

        # === DANE Z PDF ===
        # General Data
        data.card_no = self._extract(text, r"Card No\s*:\s*([^\n]+)")
        data.article_index = self._extract(text, r"Article index\s*:\s*([^\n]+)")
        data.client_article_index = self._extract(text, r"Client'?s?\s+article index\s*:\s*([^\n]+)")
        data.article_description = self._extract(text, r"Article description\s*:\s*([^\n]+)")
        data.product_structure = self._extract(text, r"Product structure\s*:\s*([^\n]+)")
        data.structure_thickness = self._extract(text, r"Structure thickness\s*:\s*([^\n]+)")
        data.structure_description = self._extract(text, r"Structure description\s*:\s*([^\n]+?)(?:\n|Chemical)")
        data.chemical_composition = self._extract(text, r"Chemical composition\s*:\s*([^\n]+)")

        # Physico-chemical properties (tylko wartości liczbowe)
        data.gramatura = self._extract_param_value(text, r"Gramatur/Weight")
        data.otr = self._extract_param_value(text, r"OTR")
        data.wvtr = self._extract_param_value(text, r"WVTR")
        data.thickness = self._extract_param_value(text, r"Grub\./Thickness")

        # Print details
        data.print_type = self._extract(text, r"Print type\s*:\s*([^\n]+)")
        data.number_of_colours = self._extract(text, r"Number of colours\s*:\s*([^\n]+)")
        data.solid_lacquer = self._extract(text, r"Solid/Lacquer\s*:\s*([^\n]+)")

        # Packing
        data.winding_code = self._extract(text, r"Winding code\s*:\s*([^\n]+)")
        data.external_diameter = self._extract(text, r"External diameter\s*:\s*([^\n]+)")
        data.width_of_core = self._extract(text, r"Width of core\s*:\s*([^\n]+)")
        data.core_submission = self._extract(text, r"Core submission\s*:\s*([^\n]+)")

        return data

    def _extract(self, text: str, pattern: str) -> str:
        """Pomocnicza metoda do ekstrakcji tekstu"""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            result = match.group(1).strip()
            return re.sub(r'\s+', ' ', result)
        return ""

    def _extract_param_value(self, text: str, param_name: str) -> str:
        """Wyciąga wartość parametru z tabeli (pierwsza liczba)"""
        pattern = rf"{param_name}.*?(\d+(?:[.,]\d+)?)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).replace(',', '.') if match else ""


# ============================================================================
# FACADE PATTERN - Uproszczony interfejs
# ============================================================================

class PDFImportService:
    """
    Facade Pattern: Uproszczony interfejs do importu danych z PDF
    """

    def __init__(
            self,
            text_extractor: ITextExtractor,
            data_parser: IDataParser,
            data_enricher: IDataEnricher,
            model_mapper: IModelMapper,
            repository: SQLiteKartaRepository
    ):
        self.text_extractor = text_extractor
        self.data_parser = data_parser
        self.data_enricher = data_enricher
        self.model_mapper = model_mapper
        self.repository = repository

    def import_pdf(self, pdf_path: Path, prepared_by: str) -> bool:
        """Importuje pojedynczy plik PDF do bazy danych"""
        try:
            # 1. Ekstrakcja tekstu
            text = self.text_extractor.extract_text(pdf_path)

            # 2. Parsowanie danych z PDF
            data = self.data_parser.parse(text, pdf_path.stem)
            data.prepared_by = prepared_by

            # 3. Wzbogacenie danych z Excel (opcjonalnie)
            data = self.data_enricher.enrich(data)

            # 4. Mapowanie na model - TYLKO dane z PDF
            karta = self.model_mapper.map_to_karta(data)

            # 5. Zapis do bazy
            self.repository.save(karta)

            # Wyświetl wyekstrahowane dane
            print(f"  ✓ Card No: {data.card_no}")
            print(f"  ✓ Article Index: {data.article_index}")
            print(f"  ✓ Client Index: {data.client_article_index}")

            return True

        except Exception as e:
            print(f"  ✗ Błąd: {e}")
            import traceback
            traceback.print_exc()
            return False

    def import_directory(self, directory: Path, prepared_by: str) -> Dict[str, int]:
        """Importuje wszystkie pliki PDF z katalogu"""
        pdf_files = list(directory.glob("*.pdf"))

        if not pdf_files:
            print(f"⚠ Nie znaleziono plików PDF w: {directory}")
            return {'success': 0, 'failed': 0}

        print(f"📄 Znaleziono {len(pdf_files)} plików PDF")
        print("=" * 70)

        stats = {'success': 0, 'failed': 0}

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")
            print("-" * 70)

            if self.import_pdf(pdf_file, prepared_by):
                stats['success'] += 1
            else:
                stats['failed'] += 1

        return stats


# ============================================================================
# FACTORY PATTERN
# ============================================================================


class PDFImportServiceFactory:
    """Factory Pattern: Tworzenie skonfigurowanego serwisu importu"""

    @staticmethod
    def create(excel_path: Optional[Path] = None) -> PDFImportService:
        """Tworzy w pełni skonfigurowany serwis importu PDF"""
        text_extractor = PDFTextExtractor()
        data_parser = RegexDataParser()
        data_enricher = ExcelDataEnricher(excel_path)
        model_mapper = MinimalKartaMapper()
        repository = SQLiteKartaRepository()

        return PDFImportService(
            text_extractor=text_extractor,
            data_parser=data_parser,
            data_enricher=data_enricher,
            model_mapper=model_mapper,
            repository=repository
        )