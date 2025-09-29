from dataclasses import dataclass


@dataclass
class ProductSpecification:
    """Klasa przechowująca specyfikację produktu"""
    # Podstawowe dane
    card_no: str = ""
    article_index: str = ""
    client_article_index: str = ""
    article_description: str = ""
    product_structure: str = ""
    structure_thickness: str = ""
    structure_description: str = ""
    chemical_composition: str = ""

    # Parametry fizykochemiczne
    gramatura_value: str = ""
    gramatura_minus: str = ""
    gramatura_plus: str = ""
    gramatura_unit: str = ""

    otr_value: str = ""
    otr_minus: str = ""
    otr_plus: str = ""
    otr_unit: str = ""

    wvtr_value: str = ""
    wvtr_minus: str = ""
    wvtr_plus: str = ""
    wvtr_unit: str = ""

    thickness_value: str = ""
    thickness_minus: str = ""
    thickness_plus: str = ""
    thickness_unit: str = ""

    # Szczegóły druku
    print_type: str = ""
    number_of_colours: str = ""
    solid_lacquer: str = ""

    # Pakowanie
    winding_code: str = ""
    external_diameter: str = ""
    width_of_core: str = ""
    core_submission: str = ""

    # Metadata
    prepared_by: str = ""
    date: str = ""
    source_file: str = ""
