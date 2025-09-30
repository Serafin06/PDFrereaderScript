
from typing import Optional, Dict

from interfaces import IDataEnricher
from tempDataBase import ExtractedPDFData


class ExcelDataEnricher(IDataEnricher):
    """Single Responsibility: Wzbogacanie danych z pliku Excel"""

    def __init__(self, excel_path: Optional[Path] = None):
        self.excel_data = None

        if excel_path and excel_path.exists():
            import pandas as pd
            self.excel_data = pd.read_excel(excel_path)
            print(f"✓ Załadowano Excel: {len(self.excel_data)} rekordów\n")

    def enrich(self, data: ExtractedPDFData) -> ExtractedPDFData:
        """Wzbogaca dane z Excela (jeśli dostępne)"""
        if self.excel_data is None:
            return data

        excel_row = self._find_matching_row(data.source_file, data.article_index)

        if excel_row is not None:
            # Możesz tutaj nadpisać/uzupełnić dane z Excela
            # Przykład: if 'gramatura' in excel_row: data.gramatura = str(excel_row['gramatura'])
            print(f"  ℹ Znaleziono dopasowanie w Excel")

        return data

    def _find_matching_row(self, filename: str, article_index: str) -> Optional[Dict]:
        """Znajduje wiersz w Excel pasujący do danych"""
        mask = self.excel_data.astype(str).apply(
            lambda row: filename in row.values or article_index in row.values,
            axis=1
        )

        matching = self.excel_data[mask]
        return matching.iloc[0].to_dict() if not matching.empty else None