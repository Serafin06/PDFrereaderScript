from abc import abstractmethod, ABC
from pathlib import Path

from tempDataBase import PDFData


class ITextExtractor(ABC):
    """Interface dla ekstrakcji tekstu"""

    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        pass


class IDataParser(ABC):
    """Interface dla parsowania danych"""

    @abstractmethod
    def parse(self, text: str) -> PDFData:
        pass


class IDataEnricher(ABC):
    """Interface dla wzbogacania danych z Excel"""

    @abstractmethod
    def enrich(self, data: PDFData, filename: str) -> PDFData:
        pass


class IGUIAutomator(ABC):
    """Interface dla automatyzacji GUI"""

    @abstractmethod
    def fill_form(self, data: PDFData) -> None:
        pass

    @abstractmethod
    def generate_pdf(self) -> None:
        pass