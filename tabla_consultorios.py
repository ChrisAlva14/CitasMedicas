NUM_CONSULTORIOS = 4

CONSULTORIOS = [
    "Medicina General",          # consultorio 0
    "Pediatría",                 # consultorio 1
    "Ginecología y Obstetricia",  # consultorio 2
    "Medicina Interna",          # consultorio 3
]


class TablaConsultorios:
    """Tabla hash de tamaño fijo con listas enlazadas en cada consultorio."""

    def __init__(self):
        # HASH ABIERTO: cada posición guarda la cabeza de una lista enlazada.
        # La tabla nunca cambia de tamaño.
        self.consultorios = [None] * NUM_CONSULTORIOS
        self.total_pacientes = 0

    # ------------------------------------------------------------------
    # FUNCIÓN HASH
    # ------------------------------------------------------------------
    def funcion_hash(self, dui_numerico):
        """Devuelve el consultorio correspondiente: dui_numerico % 4."""
        return dui_numerico % NUM_CONSULTORIOS

    # ------------------------------------------------------------------
    # INSERCIÓN
    # ------------------------------------------------------------------
    def insertar(self, paciente):
        """Inserta al paciente al inicio de la cadena de su consultorio.

        Devuelve una tupla (número de consultorio, hubo_colisión).
        Lanza ValueError si el DUI ya está registrado.
        """
        box = self.funcion_hash(paciente.dui_numerico())

        # Recorremos SOLO la cadena de ese consultorio para evitar duplicados.
        actual = self.consultorios[box]
        while actual is not None:
            if actual.dui == paciente.dui:
                raise ValueError(f"El DUI {paciente.dui} ya tiene una cita registrada.")
            actual = actual.siguiente

        # HASH ABIERTO: si la posición ya tiene pacientes, hay colisión y el
        # nuevo nodo se encadena en la misma lista. No se busca otro consultorio.
        hubo_colision = self.consultorios[box] is not None
        paciente.siguiente = self.consultorios[box]   # el anterior queda detrás
        self.consultorios[box] = paciente             # inserción al inicio, O(1)
        self.total_pacientes += 1

        return box, hubo_colision

    # ------------------------------------------------------------------
    # BÚSQUEDA
    # ------------------------------------------------------------------
    def buscar(self, dui):
        """Busca un DUI recorriendo únicamente la cadena de su consultorio.

        Devuelve (paciente, consultorio, personas_por_delante).
        Si no existe, paciente es None.
        """
        try:
            box = self.funcion_hash(int(dui.replace("-", "")))
        except (ValueError, AttributeError):
            return None, -1, 0

        # HASH ABIERTO: el DUI solo puede estar en la lista de este consultorio.
        actual = self.consultorios[box]
        por_delante = 0
        while actual is not None:
            if actual.dui == dui:
                return actual, box, por_delante
            actual = actual.siguiente       # puntero temporal al siguiente nodo
            por_delante += 1

        return None, box, por_delante

    # ------------------------------------------------------------------
    # ELIMINACIÓN
    # ------------------------------------------------------------------
    def eliminar(self, dui):
        """Desenlaza al paciente de la cadena de su consultorio.

        Devuelve el paciente eliminado o None si no existe.
        """
        try:
            box = self.funcion_hash(int(dui.replace("-", "")))
        except (ValueError, AttributeError):
            return None

        # HASH ABIERTO: solo se recorre la lista del consultorio calculado.
        actual = self.consultorios[box]
        previo = None

        while actual is not None:
            if actual.dui == dui:
                if previo is None:
                    # El paciente era la cabeza de la lista.
                    self.consultorios[box] = actual.siguiente
                else:
                    # Se salta al nodo eliminado: previo -> actual.siguiente
                    previo.siguiente = actual.siguiente
                actual.siguiente = None
                self.total_pacientes -= 1
                return actual

            previo = actual
            actual = actual.siguiente

        return None

    # ------------------------------------------------------------------
    # RECORRIDOS Y REPORTES
    # ------------------------------------------------------------------
    def contar_consultorio(self, box):
        """Cuenta cuántos pacientes hay en la cadena de un consultorio."""
        cantidad = 0
        actual = self.consultorios[box]
        while actual is not None:
            cantidad += 1
            actual = actual.siguiente
        return cantidad
