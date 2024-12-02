from enum import Enum
class CreditCardCompany(str, Enum):
    '''
    Enumeration of allowed credit card names.
    Using Enum ensures only these specific values are allowed.
    '''
    RBC= "RBC Credit Card"
    TD= "TD Credit Card"
    BMO= "BMO Credit Card"
    AMEX= "AMEX Credit Card"
    SCOTIA= "Scotia Credit Card"
    CIBC= "CIBC Credit Card"
    PC_OPTIMUM= "PC Optimum Credit Card"
    TANGERINE= "Tangerine Credit Card"
    KOHO= "Koho Credit Card"
    CAPITAL_ONE= "Capital One Credit Card"
