from dataclasses import dataclass


@dataclass
class ExtractedPDFData:
    """DTO dla danych wyciągniętych TYLKO z PDF"""
    # General Data - z PDF
    card_no: str = ""
    article_index: str = ""
    client_article_index: str = ""
    article_description: str = ""
    product_structure: str = ""
    structure_thickness: str = ""
    structure_description: str = ""
    chemical_composition: str = ""

    # Physico-chemical properties - z PDF (tylko wartości)
    gramatura: str = ""
    otr: str = ""
    wvtr: str = ""
    thickness: str = ""

    # Print details - z PDF
    print_type: str = ""
    number_of_colours: str = ""
    solid_lacquer: str = ""

    # Packing - z PDF
    winding_code: str = ""
    external_diameter: str = ""
    width_of_core: str = ""
    core_submission: str = ""

    # Metadata
    prepared_by: str = ""
    source_file: str = ""
