from pathlib import Path




"""
def main():
    #Główna funkcja - import danych z PDF do bazy

    # === KONFIGURACJA ===
    PDF_FOLDER = Path("pdfs_input")
    EXCEL_FILE = Path("parametry.xlsx")  # Opcjonalnie
    PREPARED_BY = "Twoje Imię Nazwisko"  # Zmień na swoje dane

    # Walidacja
    if not PDF_FOLDER.exists():
        print(f"❌ Folder {PDF_FOLDER} nie istnieje!")
        PDF_FOLDER.mkdir(parents=True)
        print(f"✓ Utworzono folder {PDF_FOLDER}")
        print(f"  Wrzuć tam pliki PDF i uruchom ponownie")
        return

    # Tworzenie serwisu
    excel_path = EXCEL_FILE if EXCEL_FILE.exists() else None
    service = PDFImportServiceFactory.create(excel_path)

    # Import
    print("🚀 IMPORT DANYCH Z PDF DO BAZY")
    print("=" * 70)
    print("Uwaga: Zapisywane są TYLKO dane z PDF.")
    print("Pozostałe pola uzupełni program GUI po wczytaniu.\n")

    stats = service.import_directory(PDF_FOLDER, PREPARED_BY)

    # Podsumowanie
    print("\n" + "=" * 70)
    print("📊 PODSUMOWANIE")
    print("=" * 70)
    print(f"✓ Sukces: {stats['success']}")
    print(f"✗ Błędy: {stats['failed']}")
    print(f"\n💾 Dane zapisane w bazie danych SQLite")
    print("\n📋 NASTĘPNE KROKI:")
    print("1. Uruchom GUI swojego programu")
    print("2. Wczytaj kartę po numerze (Card No)")
    print("3. Program automatycznie uzupełni domyślne wartości")
    print("4. Kliknij 'Generuj PDF'")
"""

if __name__ == "__main__":
    print("Ten skrypt wymaga integracji z GUI.")
    print("Użyj: integrate_with_gui(main_window)")