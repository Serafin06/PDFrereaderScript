from abc import abstractmethod, ABC


class ITextExtractor(ABC):
    """Interface dla ekstraktorów tekstu"""

    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Wyciąga tekst z pliku"""
        pass


class IDataParser(ABC):
    """Interface dla parserów danych"""

    @abstractmethod
    def parse(self, text: str, file_name: str) -> ExtractedPDFData:
        """Parsuje tekst do struktury danych"""
        pass


class IDataEnricher(ABC):
    """Interface dla wzbogacania danych"""

    @abstractmethod
    def enrich(self, data: ExtractedPDFData) -> ExtractedPDFData:
        """Wzbogaca dane z zewnętrznych źródeł (Excel)"""
        pass


class IModelMapper(ABC):
    """Interface dla mapowania DTO na modele domenowe"""

    @abstractmethod
    def map_to_karta(self, data: ExtractedPDFData) -> KartaWyrobu:
        """Mapuje ExtractedPDFData na KartaWyrobu - TYLKO z danymi z PDF"""
        pass