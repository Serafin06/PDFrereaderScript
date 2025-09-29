from pathlib import Path

from model import PDFSpecificationExtractor


def main():
    """Główna funkcja uruchamiająca ekstrakcję"""

    # === KONFIGURACJA ===
    PDF_FOLDER = "pdfs_input"  # Folder z plikami PDF
    EXCEL_FILE = "parametry.xlsx"  # Opcjonalnie: plik Excel z dodatkowymi danymi
    OUTPUT_FOLDER = "output"  # Folder na wyniki

    # Inicjalizacja ekstraktora
    extractor = PDFSpecificationExtractor(
        pdf_folder=PDF_FOLDER,
        excel_file=EXCEL_FILE if Path(EXCEL_FILE).exists() else None,
        output_folder=OUTPUT_FOLDER
    )

    # Przetwórz wszystkie PDF-y
    print("=" * 60)
    print("EKSTRAKCJA DANYCH Z PLIKÓW PDF")
    print("=" * 60 + "\n")

    specifications = extractor.process_all_pdfs()

    # Wyświetl wyniki
    if not specifications.empty:
        print("\n" + "=" * 60)
        print(f"PODSUMOWANIE: Wyekstrahowano {len(specifications)} specyfikacji")
        print("=" * 60)

        # Zapisz wyniki
        extractor.save_results(specifications, format="all")

        # Wyświetl przykładowe dane
        print("\n--- Przykładowe dane (pierwsze 3 kolumny) ---")
        print(specifications[['card_no', 'article_index', 'client_article_index']].head())

    else:
        print("\n⚠ Nie udało się wyekstrahować żadnych danych")


if __name__ == "__main__":
    main()