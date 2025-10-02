from dataclasses import dataclass


@dataclass
class PDFData:
    """DTO - dane wyciągnięte z PDF"""
    # General Data
    card_no: str = ""
    article_index: str = ""
    client_article_index: str = ""
    article_description: str = ""
    product_structure: str = ""
    structure_thickness: str = ""
    structure_description: str = ""
    chemical_composition: str = ""

    # Physico-chemical properties (tylko wartości)
    gramatura: str = ""
    otr: str = ""
    wvtr: str = ""
    thickness: str = ""

    # Print details
    print_type: str = ""
    number_of_colours: str = ""
    solid_lacquer: str = ""

    # Packing
    winding_code: str = ""
    core: str = ""
    external_diameter: str = ""
    width_of_core: str = ""
    core_submission: str = ""

    # Metadata
    prepared_by: str = ""
