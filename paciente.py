"""Nodo de la lista enlazada que representa a un paciente."""


class Paciente:
    """Un paciente es un nodo dentro de la cadena de su consultorio.

    El atributo ``siguiente`` es el puntero que permite el encadenamiento
    del hashing abierto (encadenamiento separado).
    """

    def __init__(self, dui, nombre, telefono, departamento, institucion, motivo, prioridad):
        self.dui = dui
        self.nombre = nombre
        self.telefono = telefono
        self.departamento = departamento
        self.institucion = institucion
        self.motivo = motivo
        self.prioridad = prioridad
        # Puntero al siguiente paciente que cayó en el mismo consultorio.
        self.siguiente = None

    def dui_numerico(self):
        """Devuelve el DUI sin guion como entero.

        Ejemplo: "04567812-3" -> 45678123. Ese número es el que se usa
        para calcular el consultorio con la función hash.
        """
        return int(self.dui.replace("-", ""))

    def __str__(self):
        return (
            f"DUI: {self.dui} | Nombre: {self.nombre} | Teléfono: {self.telefono} | "
            f"Departamento: {self.departamento} | Institución: {self.institucion} | "
            f"Motivo: {self.motivo} | Prioridad: {self.prioridad}"
        )
