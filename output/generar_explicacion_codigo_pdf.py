from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "explicacion_codigo_sistema_turnos.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles["Title"].fontName = "Helvetica-Bold"
    styles["Title"].fontSize = 19
    styles["Title"].leading = 23
    styles["Title"].alignment = TA_CENTER
    styles["Heading1"].fontName = "Helvetica-Bold"
    styles["Heading1"].fontSize = 15
    styles["Heading1"].leading = 18
    styles["Heading1"].spaceBefore = 12
    styles["Heading1"].spaceAfter = 7
    styles["Heading2"].fontName = "Helvetica-Bold"
    styles["Heading2"].fontSize = 12
    styles["Heading2"].leading = 15
    styles["Heading2"].spaceBefore = 9
    styles["Heading2"].spaceAfter = 5
    styles["BodyText"].fontName = "Helvetica"
    styles["BodyText"].fontSize = 9.4
    styles["BodyText"].leading = 12.6
    styles["BodyText"].spaceAfter = 4
    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        name="CodeBlock",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7,
        leading=8.6,
        leftIndent=6,
        rightIndent=6,
        backColor=colors.HexColor("#F3F4F6"),
        borderColor=colors.HexColor("#D1D5DB"),
        borderWidth=0.35,
        borderPadding=5,
    ))
    return styles


STYLES = build_styles()


def p(text, style="BodyText"):
    return Paragraph(text, STYLES[style])


def code(text):
    return Preformatted(text.strip(), STYLES["CodeBlock"])


def bullets(items):
    return ListFlowable(
        [ListItem(p(item), leftIndent=12) for item in items],
        bulletType="bullet",
        leftIndent=14,
    )


def table(rows, widths=None):
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(1.5 * cm, 1.0 * cm, "Explicacion del codigo - Sistema Municipal de Turnos")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def add_method(story, name, explanation, details=None):
    story.append(p(f"<b>{name}</b>", "Heading2"))
    story.append(p(explanation))
    if details:
        story.append(bullets(details))


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.7 * cm,
        title="Explicacion del codigo - Sistema Municipal de Turnos",
        author="Joaquin Cortez",
    )

    story = []
    story.append(p("Explicacion del Codigo", "Title"))
    story.append(Spacer(1, 0.15 * cm))
    story.append(p("<b>Sistema Municipal de Turnos - Java, Swing, SOLID/LSP y Supabase</b>", "Heading2"))
    story.append(p("Este documento explica el proyecto archivo por archivo y metodo por metodo, con foco en como se conectan la interfaz grafica, la logica de negocio, el principio de Liskov y la persistencia en Supabase."))

    story.append(p("1. Vista general de la arquitectura", "Heading1"))
    story.append(p("El proyecto esta dividido en capas simples para que cada parte tenga una responsabilidad clara."))
    story.append(table([
        ["Capa", "Archivos", "Responsabilidad"],
        ["Entrada", "Main.java", "Arranca la aplicacion Swing y conecta dependencias."],
        ["Interfaz grafica", "SistemaTurnosFrame.java", "Pantallas, botones, tabla y mensajes al usuario."],
        ["Logica de negocio", "GestorTurnos.java", "Crea turnos, calcula fechas, costos y descuentos."],
        ["Acceso a datos", "SupabaseClient.java", "Hace GET, POST y PATCH contra Supabase REST API."],
        ["Modelo SOLID", "TurnoMunicipal, TurnoArancelado, TurnoLicencia, TurnoSocial", "Representa los tipos de turno y demuestra Liskov."],
        ["DTOs", "SolicitudTurno, ResultadoTurno, Ciudadano, TurnoDetalle", "Transportan datos entre capas."],
    ], [3.4 * cm, 5.2 * cm, 7.6 * cm]))

    story.append(p("Flujo general", "Heading2"))
    story.append(bullets([
        "El usuario usa la ventana Swing.",
        "La ventana arma una SolicitudTurno con los datos ingresados.",
        "GestorTurnos decide que tipo de turno crear, calcula fecha, monto y descuento.",
        "SupabaseClient guarda o consulta datos en Supabase.",
        "La interfaz muestra el resultado en pantalla o en una tabla.",
    ]))

    story.append(PageBreak())
    story.append(p("2. Main.java", "Heading1"))
    story.append(p("Este archivo quedo intencionalmente chico. Su tarea es iniciar el programa y no contener reglas de negocio. Esto responde a la devolucion de descomprimir Main."))
    add_method(story, "main(String[] args)", "Punto de entrada de la aplicacion.", [
        "Usa SwingUtilities.invokeLater para iniciar Swing en el hilo correcto de interfaz grafica.",
        "Configura el Look and Feel del sistema operativo.",
        "Crea SupabaseClient, que sabe comunicarse con la base.",
        "Crea GestorTurnos, que contiene la logica de negocio.",
        "Crea SistemaTurnosFrame y lo muestra.",
        "Si falta una variable de entorno o ocurre otro error al iniciar, muestra un JOptionPane con el problema.",
    ])
    story.append(code("""
SupabaseClient supabaseClient = new SupabaseClient();
GestorTurnos gestorTurnos = new GestorTurnos(supabaseClient);
new SistemaTurnosFrame(gestorTurnos).setVisible(true);
"""))

    story.append(p("3. Interfaces del modelo", "Heading1"))
    story.append(p("Estas interfaces son la base de la aplicacion del principio de Sustitucion de Liskov."))
    add_method(story, "TurnoMunicipal.getDetalleTurno()", "Obliga a cualquier turno municipal a devolver una descripcion legible del tramite.")
    add_method(story, "TurnoMunicipal.getFechaHora()", "Obliga a cualquier turno a exponer la fecha y hora asignada.")
    add_method(story, "TurnoMunicipal.confirmarTurno()", "Define una accion comun: confirmar el turno. Cada tipo lo implementa con su mensaje propio.")
    add_method(story, "TurnoArancelado.calcularCosto()", "Solo existe para turnos pagos. No se fuerza a TurnoSocial a tener costo.")
    add_method(story, "TurnoArancelado.generarBoletoPago()", "Representa el comportamiento especifico de un tramite arancelado.")
    story.append(p("Punto clave: TurnoArancelado extiende TurnoMunicipal. Por eso todo turno arancelado tambien es municipal, pero no todo turno municipal es arancelado."))

    story.append(p("4. Modelos: TurnoLicencia y TurnoSocial", "Heading1"))
    add_method(story, "TurnoLicencia(String fechaHora, String categoriaLicencia)", "Constructor del turno de licencia. Guarda fecha/hora y categoria de licencia.")
    add_method(story, "TurnoLicencia.getDetalleTurno()", "Devuelve un texto como Renovacion Licencia Categ. B1.")
    add_method(story, "TurnoLicencia.getFechaHora()", "Devuelve la fecha asignada por el sistema.")
    add_method(story, "TurnoLicencia.confirmarTurno()", "Muestra que el turno de licencia fue confirmado y queda pendiente de pago.")
    add_method(story, "TurnoLicencia.calcularCosto()", "Calcula el costo del tramite. Para B1 devuelve 15000. Para otras categorias devuelve 20000.")
    add_method(story, "TurnoLicencia.generarBoletoPago()", "Muestra en consola un mensaje de boleto por el costo calculado.")
    add_method(story, "TurnoSocial(String fechaHora, String motivo)", "Constructor del turno social. Guarda fecha/hora y motivo.")
    add_method(story, "TurnoSocial.getDetalleTurno()", "Devuelve un texto indicando que es un turno social gratuito y su motivo.")
    add_method(story, "TurnoSocial.getFechaHora()", "Devuelve la fecha asignada por el sistema.")
    add_method(story, "TurnoSocial.confirmarTurno()", "Muestra que el turno social fue confirmado.")
    story.append(p("Relacion con Liskov: GestorTurnos puede trabajar con una variable TurnoMunicipal y asignarle un TurnoLicencia o un TurnoSocial sin romper el contrato comun."))

    story.append(PageBreak())
    story.append(p("5. DTOs: SolicitudTurno y ResultadoTurno", "Heading1"))
    story.append(p("Los records son contenedores de datos. Reducen codigo repetitivo porque Java genera constructor, getters, equals, hashCode y toString."))
    add_method(story, "SolicitudTurno(...)", "Representa los datos que entran desde la interfaz cuando el usuario quiere sacar un turno.", [
        "dni: identifica al ciudadano.",
        "nombreCompleto, email, telefono: datos personales.",
        "mayor65: indica si corresponde descuento.",
        "servicio: nombre del servicio elegido.",
    ])
    add_method(story, "ResultadoTurno(...)", "Representa lo que vuelve despues de guardar un turno.", [
        "idTurno: ID creado en Supabase.",
        "detalle y fechaHora: informacion del turno creado.",
        "arancelado: indica si genero pago.",
        "montoOriginal, descuentoAplicado, montoFinal: resumen economico del tramite.",
    ])

    story.append(p("6. GestorTurnos.java", "Heading1"))
    story.append(p("Esta clase concentra la logica de negocio. La GUI no calcula fechas ni descuentos; se lo pide a GestorTurnos."))
    add_method(story, "GestorTurnos(SupabaseClient supabaseClient)", "Constructor. Recibe el cliente de Supabase por parametro para poder persistir datos.")
    add_method(story, "sacarTurno(SolicitudTurno solicitud)", "Metodo principal para crear un turno.", [
        "Crea un TurnoMunicipal concreto con crearTurnoMunicipal.",
        "Calcula el monto original si el turno es arancelado.",
        "Calcula descuento si el ciudadano es mayor de 65 y el tramite es pago.",
        "Calcula monto final.",
        "Llama a SupabaseClient.registrarTurno para guardar ciudadano, turno y pago.",
        "Devuelve ResultadoTurno para que la GUI pueda mostrar un resumen.",
    ])
    add_method(story, "obtenerTurnosPorDni(String dni)", "Delega en SupabaseClient la consulta de turnos por DNI.")
    add_method(story, "buscarCiudadanoPorDni(String dni)", "Delega en SupabaseClient la busqueda de ciudadano para reutilizar datos existentes.")
    add_method(story, "pagarTurnoArancelado(String dni, int idTurno)", "Delega en SupabaseClient la operacion de marcar un turno pago.")
    add_method(story, "cancelarTurno(String dni, int idTurno)", "Delega en SupabaseClient la cancelacion logica del turno.")
    add_method(story, "obtenerServiciosDisponibles()", "Devuelve la lista de servicios que la GUI carga en el combo.")
    add_method(story, "crearTurnoMunicipal(String servicio)", "Decide que clase instanciar segun el servicio.", [
        "Si el servicio es Licencia de conducir, crea TurnoLicencia.",
        "Si el servicio es Asistencia social alimentaria, crea TurnoSocial.",
        "Si llega otro texto, lanza error de servicio no reconocido.",
    ])
    add_method(story, "asignarFechaHoraTurno(String servicio)", "Asigna fechas automaticamente.", [
        "Licencia: fecha actual + 7 dias a las 09:00.",
        "Social: fecha actual + 3 dias a las 10:30.",
        "Devuelve el formato yyyy-MM-dd HH:mm:ss para Supabase.",
    ])
    add_method(story, "calcularMontoOriginal(TurnoMunicipal turno)", "Si el turno implementa TurnoArancelado, llama calcularCosto. Si no, devuelve 0.")
    add_method(story, "calcularDescuento(TurnoMunicipal turno, boolean mayor65, double montoOriginal)", "Aplica 30% de descuento solo si el ciudadano es mayor de 65 y el turno es arancelado.")

    story.append(PageBreak())
    story.append(p("7. SistemaTurnosFrame.java", "Heading1"))
    story.append(p("Es la ventana principal Swing. Contiene tres pestanas: Sacar turno, Mis turnos y Servicios. No deberia contener reglas profundas de negocio; usa GestorTurnos para eso."))
    add_method(story, "SistemaTurnosFrame(GestorTurnos gestorTurnos)", "Constructor de la ventana.", [
        "Guarda la referencia al gestor.",
        "Configura cierre de ventana, tamano y posicion.",
        "Inicializa componentes.",
        "Carga el contenido principal con pestanas.",
    ])
    add_method(story, "configurarComponentes()", "Carga servicios en el JComboBox, bloquea areas de salida para que no sean editables y habilita ordenamiento en la tabla.")
    add_method(story, "crearContenido()", "Crea el JTabbedPane con las pestanas Sacar turno, Mis turnos y Servicios.")
    add_method(story, "crearPanelAlta()", "Arma la pestana para sacar turno.", [
        "Campos: DNI, nombre, email, telefono, mayor de 65, servicio.",
        "Boton Buscar ciudadano.",
        "Boton Sacar turno.",
        "Boton Limpiar formulario.",
        "Area de salida con resumen del turno creado.",
    ])
    add_method(story, "crearPanelConsulta()", "Arma la pestana para consultar, pagar y cancelar turnos.", [
        "Campo DNI.",
        "Tabla de turnos.",
        "Botones Ver mis turnos, Marcar pagado y Cancelar turno.",
    ])
    add_method(story, "crearPanelServicios()", "Arma una pestana informativa con los servicios disponibles y sus condiciones.")
    add_method(story, "addField(...)", "Metodo auxiliar para agregar una etiqueta y un campo al formulario usando GridBagLayout.")
    add_method(story, "buscarCiudadano()", "Busca el ciudadano por DNI.", [
        "Valida que el DNI no este vacio.",
        "Llama a gestorTurnos.buscarCiudadanoPorDni en segundo plano.",
        "Si existe, completa campos y los bloquea para no duplicar datos.",
        "Si no existe, desbloquea campos para crear el ciudadano.",
    ])
    add_method(story, "sacarTurno()", "Lee datos del formulario y crea una SolicitudTurno.", [
        "Valida DNI y nombre.",
        "Llama a gestorTurnos.sacarTurno.",
        "Muestra el ResultadoTurno formateado.",
    ])
    add_method(story, "cargarTurnos()", "Consulta turnos por DNI y los carga en la tabla.")
    add_method(story, "pagarTurnoSeleccionado()", "Obtiene el ID de la fila seleccionada y marca el turno arancelado como pagado.")
    add_method(story, "cancelarTurnoSeleccionado()", "Obtiene el ID de la fila seleccionada y marca el turno como Cancelado.")
    add_method(story, "obtenerIdSeleccionado()", "Convierte la fila seleccionada de la JTable al indice real del modelo y devuelve el ID de turno.")
    add_method(story, "mostrarTurnos(List<TurnoDetalle> turnos)", "Limpia la tabla y agrega una fila por cada turno con datos de servicio, estado, descuento y pago.")
    add_method(story, "formatearResultado(ResultadoTurno resultado)", "Construye el texto que se muestra al crear un turno. Si es arancelado muestra monto, descuento y total.")
    add_method(story, "limpiarAlta()", "Limpia el formulario de alta y vuelve a habilitar los campos.")
    add_method(story, "bloquearDatosCiudadano()", "Deshabilita edicion de datos cuando el ciudadano ya existe.")
    add_method(story, "desbloquearDatosCiudadano()", "Habilita edicion cuando el ciudadano no existe o se limpia el formulario.")
    add_method(story, "ejecutarAsync(Operacion operacion)", "Ejecuta operaciones lentas en un Thread aparte para no congelar la interfaz Swing.")
    add_method(story, "mostrarError(String mensaje)", "Muestra errores en un JOptionPane.")
    add_method(story, "Operacion", "Interfaz funcional interna usada por ejecutarAsync para recibir acciones que pueden lanzar excepciones.")

    story.append(PageBreak())
    story.append(p("8. SupabaseClient.java", "Heading1"))
    story.append(p("Es la capa de acceso a datos. Construye peticiones HTTP para Supabase REST. No tiene pantallas ni reglas visuales."))
    add_method(story, "readRequiredEnv(String name)", "Lee variables de entorno obligatorias.", [
        "SUPABASE_URL debe tener la URL base, sin /rest/v1.",
        "SUPABASE_SERVICE_ROLE_KEY debe tener la secret key.",
        "Si falta una variable, lanza IllegalStateException.",
        "Si la URL termina en /, lo quita para evitar doble barra.",
    ])
    add_method(story, "registrarTurno(...) version antigua", "Metodo de compatibilidad. Llama a la version nueva con mayor65 false y montos 0.")
    add_method(story, "registrarTurno(...) version nueva", "Guarda un turno completo.", [
        "Busca o crea ciudadano.",
        "Busca o crea servicio.",
        "Crea turno.",
        "Si el servicio es arancelado, crea pago con monto original, descuento y monto final.",
        "Devuelve el ID del turno creado.",
    ])
    add_method(story, "obtenerTurnosPorDni(String dni)", "Consulta turnos de un ciudadano usando relaciones REST.", [
        "Consulta turnos.",
        "Incluye servicios, pagos y ciudadanos mediante select relacional.",
        "Filtra por ciudadanos.dni.",
        "Ordena por fecha_hora descendente.",
        "Convierte JSON a lista de TurnoDetalle.",
    ])
    add_method(story, "buscarCiudadanoPorDni(String dni)", "Consulta datos del ciudadano por DNI. Devuelve null si no existe.")
    add_method(story, "pagarTurnoArancelado(String dni, int idTurno)", "Marca como pagado sin eliminar.", [
        "Primero trae los turnos del DNI.",
        "Verifica que el ID pertenezca al ciudadano.",
        "Verifica que sea arancelado.",
        "Actualiza pagos.estado_pago a Pagado y fecha_pago a la fecha actual.",
        "Actualiza turnos.estado a Pagado.",
    ])
    add_method(story, "cancelarTurno(String dni, int idTurno)", "Valida que el turno pertenezca al DNI y actualiza turnos.estado a Cancelado.")
    add_method(story, "buscarOCrearCiudadano(...)", "Busca ciudadano por DNI. Si existe devuelve su ID. Si no existe, arma JSON y lo inserta en ciudadanos.")
    add_method(story, "buscarServicio(String nombreServicio)", "Busca el servicio por nombre. Si no existe, llama a crearServicio.")
    add_method(story, "crearServicio(String nombreServicio)", "Crea Licencia de conducir o Asistencia social alimentaria con sus valores base.")
    add_method(story, "crearTurno(...)", "Inserta en turnos id_ciudadano, id_servicio, fecha_hora y estado Pendiente. Devuelve id_turno.")
    add_method(story, "crearPago(...)", "Inserta en pagos id_turno, monto_original, descuento_aplicado, monto_final y estado_pago Pendiente.")
    add_method(story, "get(String path) / get(String path, String dni)", "Construye y envia una peticion HTTP GET.")
    add_method(story, "post(String path, String body, String dni)", "Construye y envia una peticion HTTP POST con JSON. Usa Prefer: return=representation para que Supabase devuelva el registro creado.")
    add_method(story, "patch(String path, String body, String dni)", "Construye y envia una peticion HTTP PATCH para actualizar registros sin borrarlos.")
    add_method(story, "requestBuilder(String path, String dni)", "Centraliza headers y URL.", [
        "Agrega apikey con la secret key.",
        "Si la key es legacy JWT empieza con eyJ y agrega Authorization Bearer.",
        "Si se pasa DNI, agrega header x-dni.",
    ])
    add_method(story, "send(HttpRequest request)", "Ejecuta la peticion HTTP. Si el status no es 2xx, lanza IOException con el cuerpo del error.")
    add_method(story, "encode(String value)", "Codifica valores para URL, reemplazando espacios por %20.")
    add_method(story, "escapeJson(String value)", "Escapa barras y comillas para evitar romper el JSON construido manualmente.")
    add_method(story, "extractObjects(String jsonArray)", "Separa objetos dentro de una respuesta JSON tipo array.")
    add_method(story, "extractInt / extractNullableInt", "Extraen enteros desde JSON. La version nullable devuelve null si no encuentra el campo.")
    add_method(story, "extractString / extractNullableString", "Extraen textos desde JSON.")
    add_method(story, "extractBoolean", "Extrae booleanos true/false desde JSON.")
    add_method(story, "extractDouble / extractNullableDouble", "Extraen numeros decimales desde JSON.")
    add_method(story, "ServicioMunicipal", "Record privado para manejar internamente datos de la tabla servicios.")
    add_method(story, "TurnoDetalle", "Record publico que representa una fila de turno ya lista para mostrar en la GUI.")
    add_method(story, "Ciudadano", "Record publico que representa un ciudadano encontrado por DNI.")

    story.append(PageBreak())
    story.append(p("9. ProcesadorTurnos.java", "Heading1"))
    story.append(p("Quedo como servicio conceptual de apoyo para demostrar polimorfismo y Liskov por consola, aunque el flujo principal actual usa Swing y GestorTurnos."))
    add_method(story, "imprimirReporteTurnos(List<TurnoMunicipal> turnos)", "Recibe cualquier lista de TurnoMunicipal. Puede imprimir TurnoSocial o TurnoLicencia sin distinguir clases concretas.")
    add_method(story, "procesarPagos(List<TurnoArancelado> turnosArancelados)", "Recibe solamente turnos arancelados, por eso puede llamar generarBoletoPago con seguridad.")

    story.append(p("10. Como se aplica Liskov en este codigo", "Heading1"))
    story.append(p("El sistema respeta Liskov porque separa el contrato general de los turnos del contrato especifico de los pagos."))
    story.append(bullets([
        "TurnoMunicipal define solo lo que todo turno debe cumplir.",
        "TurnoSocial implementa TurnoMunicipal porque es gratuito y no necesita costo.",
        "TurnoLicencia implementa TurnoArancelado, que a su vez extiende TurnoMunicipal.",
        "GestorTurnos puede guardar un TurnoLicencia o TurnoSocial dentro de una variable TurnoMunicipal.",
        "El costo se calcula solo si el objeto tambien es TurnoArancelado.",
    ]))
    story.append(code("""
TurnoMunicipal turno = new TurnoLicencia(fechaHora, "B1");
// o tambien:
TurnoMunicipal turno = new TurnoSocial(fechaHora, "Asistencia alimentaria");

// En ambos casos esto funciona:
turno.getDetalleTurno();
turno.getFechaHora();

// Pero calcularCosto solo se usa si es TurnoArancelado.
"""))

    story.append(p("11. Configuracion necesaria", "Heading1"))
    story.append(p("Para ejecutar la aplicacion, IntelliJ o PowerShell deben tener estas variables de entorno:"))
    story.append(code("""
SUPABASE_URL=https://vqbdyvcmyvcyezwkxcek.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...
"""))
    story.append(p("No se debe subir la secret key al repositorio. El proyecto ya esta preparado para leerla desde variables de entorno."))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
