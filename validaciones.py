"""Datos fijos y validaciones de formato (solo biblioteca estándar)."""

DEPARTAMENTOS = [
    "Ahuachapán",
    "Cabañas",
    "Chalatenango",
    "Cuscatlán",
    "La Libertad",
    "La Paz",
    "La Unión",
    "Morazán",
    "San Miguel",
    "San Salvador",
    "San Vicente",
    "Santa Ana",
    "Sonsonate",
    "Usulután",
]

INSTITUCIONES = ["MINSAL", "ISSS", "Particular"]
PRIORIDADES = ["Alta", "Media", "Baja"]

_DIGITOS = "0123456789"


def validar_dui(texto):
    """Valida solo el formato ########-# (8 dígitos, guion y dígito verificador)."""
    texto = (texto or "").strip()
    if len(texto) != 10:
        return False
    if texto[8] != "-":
        return False
    return all(caracter in _DIGITOS for caracter in texto[:8] + texto[9])


def validar_telefono(texto):
    """Valida el formato ####-#### (8 dígitos)."""
    texto = (texto or "").strip()
    if len(texto) != 9:
        return False
    if texto[4] != "-":
        return False
    return all(caracter in _DIGITOS for caracter in texto[:4] + texto[5:])
