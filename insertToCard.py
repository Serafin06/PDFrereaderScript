
class MinimalKartaMapper(IModelMapper):
    """
    Single Responsibility: Mapowanie TYLKO danych z PDF na model KartaWyrobu
    Pozostałe pola pozostają puste - zostaną uzupełnione w GUI
    """

    def map_to_karta(self, data: ExtractedPDFData) -> KartaWyrobu:
        """Mapuje TYLKO wyekstrahowane dane z PDF"""

        # Minimalne dane - tylko producent (pusty, GUI uzupełni)
        producent = Producent(nazwa="", adres="")

        # Artykuł - TYLKO dane z PDF
        artykul = Artykul(
            nr_karty=data.card_no,
            data=datetime.now().strftime("%Y-%m-%d"),
            indeks=data.article_index,
            klienta=data.client_article_index,
            nazwa=data.article_description,
            struktura=data.product_structure,
            opis_struktury=data.structure_description,
            sklad_chemiczny=data.chemical_composition,
            grubosc_struktury=data.structure_thickness,
            specyfikacja_klienta=""  # Puste - GUI uzupełni
        )

        # Właściwości - TYLKO te z PDF
        wlasciwosci = []
        if data.gramatura:
            wlasciwosci.append(WlasciwosciFizyczne(
                nazwa="Gramatura",
                metoda="PN-81/P 50129",
                wartosc=data.gramatura,
                jednostka="g/m²"
            ))

        if data.otr:
            wlasciwosci.append(WlasciwosciFizyczne(
                nazwa="OTR (bariera O₂)",
                metoda="DIN 53380",
                wartosc=data.otr,
                jednostka="cm³/m²/24h"
            ))

        if data.wvtr:
            wlasciwosci.append(WlasciwosciFizyczne(
                nazwa="WVTR (bariera H₂O)",
                metoda="DIN 53122",
                wartosc=data.wvtr,
                jednostka="g/m²/24h"
            ))

        if data.thickness:
            wlasciwosci.append(WlasciwosciFizyczne(
                nazwa="Grubość",
                metoda="PN-ISO 4593",
                wartosc=data.thickness,
                jednostka="μm"
            ))

        # Nadruk - TYLKO dane z PDF, reszta pusta
        nadruk = Nadruk(
            rodzaj=data.print_type,
            ilosc_kolorow=data.number_of_colours,
            przyczepnosc="",  # Puste - GUI uzupełni domyślną wartością
            kolorystyka="",   # Puste - GUI uzupełni domyślną wartością
            lakier=data.solid_lacquer
        )

        # Pakowanie - TYLKO dane z PDF, reszta pusta
        pakowanie = Pakowanie(
            kod_nawoju=data.winding_code,
            waga_nawoju="",  # Puste - GUI uzupełni
            srednica_nawoju=data.external_diameter,
            rolek_paleta="",  # Puste - GUI uzupełni
            tuleja_wewnetrzna="",  # Puste - GUI uzupełni
            szerokosc_tulei=data.width_of_core,
            wysuniecie_tulei=data.core_submission,
            typ_palety="",  # Puste - GUI uzupełni
            identyfikacja="",  # Puste - GUI uzupełni domyślnym tekstem
            przechowywanie="",  # Puste - GUI uzupełni domyślnym tekstem
            okres_przydatnosci=""  # Puste - GUI uzupełni domyślną wartością
        )

        # Zastosowanie - puste, GUI uzupełni domyślnymi wartościami
        zastosowanie = Zastosowanie(opis="", dopuszczenie="")

        # Podpisy - tylko przygotował
        podpisy = PodpisyDokumentu(
            opracowal=data.prepared_by,
            zatwierdził="",
            data_opracowania=datetime.now().strftime("%Y-%m-%d"),
            data_zatwierdzenia=""
        )

        return KartaWyrobu(
            producent=producent,
            artykul=artykul,
            wlasciwosci=wlasciwosci,
            nadruk=nadruk,
            pakowanie=pakowanie,
            zastosowanie=zastosowanie,
            podpisy=podpisy
        )
