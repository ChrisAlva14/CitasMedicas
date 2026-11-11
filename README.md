# Registro de Citas Médicas - El Salvador

Aplicación de escritorio en Python con **Tkinter** que demuestra el **hashing abierto**
(encadenamiento separado con listas enlazadas) usando una unidad de salud con
**4 consultorios fijos**.

> **Aviso:** todos los datos de este documento son ficticios y no corresponden a
> personas reales. El consultorio lo decide la función hash, no la especialidad del
> motivo de consulta. Es una simulación académica.

**El programa inicia completamente vacío.** No hay pacientes precargados: se
registran uno por uno desde la pestaña **Registrar**. Los ejemplos de este README
son solo una guía para practicar.

## La ventana

La aplicación tiene una sola ventana con dos zonas:

**Izquierda, tres pestañas:**

| Pestaña | Qué hace |
|---|---|
| **Registrar** | Formulario con DUI, nombre, teléfono, departamento, institución, motivo y prioridad. Al guardar muestra el cálculo `DUI % 4`, el consultorio y si hubo colisión. |
| **Consultar** | Busca una cita por DUI y muestra su posición en la fila y cuántas personas tiene por delante. |
| **Cancelar / Atender** | Busca la cita, la muestra y permite eliminarla con confirmación. El nodo se desenlaza de la cadena. |

**Derecha, la tabla hash dibujada:**

- Una fila por consultorio, con sus nodos unidos por flechas y terminados en `NULL`.
- Etiqueta `COLISIÓN` cuando una cadena tiene 2 o más pacientes.
- Total de pacientes, conteo por consultorio y fila más larga.
- Botón **Resumen detallado** con los totales por departamento.

Los colores del dibujo ayudan a explicar el hashing abierto:

| Color / marca | Significado |
|---|---|
| Recuadro amarillo | Nodo recién insertado. |
| Recuadro verde | Nodo encontrado por una búsqueda. |
| Recuadro azul claro | Nodo normal de la cadena. |
| Etiqueta `COLISIÓN` | Ese consultorio ya tenía pacientes y el nuevo se encadenó. |
| `NULL` | Fin de la lista enlazada. |

## Cómo se aplica el hashing abierto

La tabla hash es un arreglo de tamaño fijo `m = 4`. Cada posición representa un
consultorio y guarda la **cabeza de una lista enlazada**:

| Posición (Índice) | Consultorio en pantalla |
|---|---|
| 0 | Consultorio 1 |
| 1 | Consultorio 2 |
| 2 | Consultorio 3 |
| 3 | Consultorio 4 |

La función hash toma el DUI sin guion como entero y calcula:

```text
consultorio = dui_numerico % 4
```

Ejemplo: `04567812-3` → `45678123` → `45678123 % 4 = 3` → Posición 3 (Consultorio 4).

Al convertir el DUI a entero se pierden los ceros a la izquierda, pero el resultado
del módulo es el mismo. Si un paciente cae en un consultorio que ya tiene pacientes,
**no se mueve a otro consultorio libre**: se agrega a la lista de ese mismo
consultorio. Eso es precisamente el hashing abierto. La tabla nunca cambia de tamaño.

## Ejemplos para ingresar manualmente

Use la pestaña **Registrar** y escriba estos 8 pacientes en el orden indicado.

| # | DUI | Nombre completo | Teléfono | Departamento | Institución | Motivo | Prioridad |
|---|---|---|---|---|---|---|---|
| 1 | `04567812-3` | María José Hernández Flores | `7781-2043` | San Salvador | MINSAL | Control prenatal | Media |
| 2 | `03124560-7` | Carlos Alberto Martínez Rivas | `6123-4598` | La Libertad | ISSS | Control de hipertensión | Media |
| 3 | `05981234-5` | Ana Lucía Rodríguez Portillo | `7011-3388` | Santa Ana | MINSAL | Control de niño sano | Baja |
| 4 | `02876541-0` | José Roberto Guevara Mejía | `7854-1122` | San Miguel | ISSS | Fiebre y sospecha de dengue | Alta |
| 5 | `06345698-2` | Karla Beatriz Menjívar Cruz | `6344-9075` | Sonsonate | MINSAL | Enfermedad respiratoria | Alta |
| 6 | `01234568-9` | Luis Fernando Amaya Quintanilla | `7566-2211` | Usulután | Particular | Dolor abdominal | Media |
| 7 | `07654320-4` | Rosa Elena Argueta Beltrán | `7033-5544` | Cuscatlán | MINSAL | Control de diabetes | Baja |
| 8 | `04412896-6` | Miguel Ángel Cañas Orellana | `7912-6677` | Ahuachapán | ISSS | Consulta general | Baja |

### Cálculo esperado del hash

| # | DUI sin guion | Operación | Consultorio asignado | ¿Colisión al ingresar? |
|---|---|---|---|---|
| 1 | `045678123` | `045678123 % 4 = 3` | Consultorio 4 | No, el consultorio estaba vacío |
| 2 | `031245607` | `031245607 % 4 = 3` | Consultorio 4 | Sí, se encadena al final |
| 3 | `059812345` | `059812345 % 4 = 1` | Consultorio 2 | No, el consultorio estaba vacío |
| 4 | `028765410` | `028765410 % 4 = 2` | Consultorio 3 | No, el consultorio estaba vacío |
| 5 | `063456982` | `063456982 % 4 = 2` | Consultorio 3 | Sí, se encadena al final |
| 6 | `012345689` | `012345689 % 4 = 1` | Consultorio 2 | Sí, se encadena al final |
| 7 | `076543204` | `076543204 % 4 = 0` | Consultorio 1 | No, el consultorio estaba vacío |
| 8 | `044128966` | `044128966 % 4 = 2` | Consultorio 3 | Sí, se encadena al final |

### Cadenas esperadas al terminar

Como la inserción es al final de la fila (**cola de espera FIFO: primero en llegar, primero en ser atendido**), los pacientes conservan su orden cronológico de llegada. El primer paciente registrado aparece a la cabeza y los posteriores se encadenan detrás:

```text
Consultorio 1: [DUI: 07654320-4] -> NULL
Consultorio 2 (COLISIÓN - 2 pacientes): [DUI: 05981234-5] -> [DUI: 01234568-9] -> NULL
Consultorio 3 (COLISIÓN - 3 pacientes): [DUI: 02876541-0] -> [DUI: 06345698-2] -> [DUI: 04412896-6] -> NULL
Consultorio 4 (COLISIÓN - 2 pacientes): [DUI: 04567812-3] -> [DUI: 03124560-7] -> NULL
```

## Cómo registrar el primer paciente

1. Abra la aplicación con `python main.py`.
2. Vaya a la pestaña **Registrar**.
3. Complete el formulario:
   - DUI: `04567812-3`
   - Nombre completo: `María José Hernández Flores`
   - Teléfono: `7781-2043`
   - Departamento: `San Salvador`
   - Institución: `MINSAL`
   - Motivo: `Control prenatal`
   - Prioridad: `Media`
4. Presione **Registrar cita**.

Debajo de los botones aparecerá:

```text
Cita registrada: María José Hernández Flores
045678123 % 4 = 3  →  Consultorio 4
El consultorio estaba vacío: el paciente es el primero en la fila.
```

El nodo se dibuja resaltado en amarillo en la fila del Consultorio 4.
Repita el proceso con los otros 7 pacientes. Si el consultorio ya tenía pacientes,
el mensaje será:

```text
¡Colisión! Se encadena al final de la fila de ese consultorio.
```

También puede presionar **Enter** dentro de un campo para registrar la cita.

## Recorrido sugerido para la exposición

1. Abra la aplicación. Las cuatro filas muestran `NULL`: la tabla está vacía.
2. Registre al paciente **1**. Como el Consultorio 4 está vacío, es el primero en la fila
   y su nodo aparecerá en amarillo.
3. Registre al paciente **2**. También cae en el Consultorio 4: hay colisión y la
   cadena queda `[04567812-3] -> [03124560-7] -> NULL` (cola de espera FIFO).
   Aunque los consultorios 1, 2 y 3 estén libres, el paciente **no se mueve**: eso
   demuestra el hashing abierto.
4. Registre los pacientes **3 al 8** y observe cómo cada uno se encadena al final de su
   consultorio.
5. En la pestaña **Consultar**, busque el DUI `04567812-3`: el nodo se marca en verde,
   aparece en el Consultorio 4, posición 1, con 0 personas por delante (es el próximo
   en ser atendido). El DUI `03124560-7` está en la posición 2, con 1 persona por delante.
6. En **Cancelar / Atender**, busque el DUI `04567812-3` (primero en la fila del
   Consultorio 4), confirme y vea cómo la cadena queda `[03124560-7] -> NULL`,
   promoviendo a Carlos Alberto al primer lugar.
7. Elimine el DUI `06345698-2`, que está en medio de la cadena del Consultorio 3
   (`[02876541-0] -> [06345698-2] -> [04412896-6]`). La cadena debe quedar
   `[02876541-0] -> [04412896-6] -> NULL`.
8. Intente registrar otra vez un DUI que ya exista: el sistema lo rechaza.
9. Observe que el motivo no decide el consultorio: Rosa Elena tiene "Control de
   diabetes" y cae en Consultorio 1; Luis Fernando tiene "Dolor abdominal" y
   cae en Consultorio 2. Lo decide únicamente `DUI % 4`.
10. Abra **Resumen detallado** para mostrar los totales por consultorio y por
    departamento.

## Operaciones

- **Insertar:** se calcula el consultorio correspondiente (`DUI % 4`). Si ya hay pacientes
  en el consultorio (colisión), el nuevo nodo se enlaza **al final de la lista**
  (comportamiento de cola de espera FIFO: primero en llegar, primero en ser atendido),
  preservando el orden de llegada para los turnos médicos.
- **Buscar:** se calcula el consultorio y se recorre solo esa lista con un puntero
  temporal. Devuelve al paciente, su consultorio y cuántas personas tiene por delante.
- **Eliminar:** se localiza el nodo con un puntero `previo`. Si es la cabeza de la fila, se
  actualiza la cabeza de la lista; si está en medio o al final, se hace
  `previo.siguiente = actual.siguiente`. Así se desenlaza el nodo y la cadena se
  reconecta.
- **Dibujar:** recorre las 4 cadenas y dibuja cada nodo con flechas hasta `NULL`.
  Marca con `COLISIÓN` los consultorios con 2 o más pacientes.
- **Resumen:** total de pacientes, pacientes por consultorio, pacientes por
  departamento y consultorio con la fila más larga.

El conteo por departamento se hace manualmente con una lista de pares
`[departamento, cantidad]`; no se usan `dict`, `set` ni bibliotecas de hash.

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Aplicación Tkinter: formularios, dibujo de la tabla hash y resumen. |
| `paciente.py` | Clase `Paciente` (nodo) con el puntero `siguiente`. |
| `tabla_consultorios.py` | Clase `TablaConsultorios`: la tabla hash y sus operaciones. |
| `validaciones.py` | Departamentos, instituciones, prioridades y validación de formatos. |
| `README.md` | Este documento con los ejemplos para ingresar manualmente. |

## Requisitos

- Python 3.8 o superior.
- Tkinter viene incluido con Python en Windows y macOS. En algunas distribuciones de
  Linux puede requerir el paquete del sistema `python3-tk` si no está instalado.
- No se necesita instalar nada más: solo se usa la biblioteca estándar.

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
python main.py
```

En Windows, si `python` no está disponible:

```bash
py main.py
```

Si no quiere que quede una ventana negra de consola detrás de la interfaz:

```bat
pythonw main.py
```

Al abrir, la tabla está vacía. Registre los pacientes con la pestaña **Registrar**;
no es necesario cargar nada antes.
