from pathlib import Path
from typing import Optional

from interface import IDataEnricher
from tempDataBase import PDFData


class ExcelDataEnricher(IDataEnricher):
    """Wzbogacanie danych z Excel (opcjonalne)"""

    def __init__(self, excel_path: Optional[Path] = None):
        self.excel_data = None
        if excel_path and excel_path.exists():
            import pandas as pd
            self.excel_data = pd.read_excel(excel_path)
            print(f"✓ Załadowano Excel: {len(self.excel_data)} rekordów\n")

    def enrich(self, data: PDFData, filename: str) -> PDFData:
        if self.excel_data is None:
            return data

        # Szukaj dopasowania
        mask = self.excel_data.astype(str).apply(
            lambda row: filename in row.values or data.article_index in row.values,
            axis=1
        )
        matching = self.excel_data[mask]

        if not matching.empty:
            excel_row = matching.iloc[0].to_dict()
            # Możesz tutaj nadpisać dane z Excela
            # Przykład: data.gramatura = str(excel_row.get('gramatura', data.gramatura))
            print(f"  ℹ Znaleziono dane w Excel")

        return data