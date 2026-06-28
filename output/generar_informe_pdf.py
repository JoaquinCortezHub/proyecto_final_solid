from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
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
OUTPUT = ROOT / "output" / "informe_proyecto_solid_turnos_municipales.pdf"
DER_IMAGE = ROOT / "src" / "com" / "municipio" / "turnos" / "relacion_entidad_actualizada.png"
REPO_URL = "https://github.com/JoaquinCortezHub/proyecto_final_solid"


def styles():
    base = getSampleStyleSheet()
    base["Title"].fontName = "Helvetica-Bold"
    base["Title"].fontSize = 20
    base["Title"].leading = 24
    base["Title"].alignment = TA_CENTER

    base["Heading1"].fontName = "Helvetica-Bold"
    base["Heading1"].fontSize = 15
    base["Heading1"].leading = 18
    base["Heading1"].spaceBefore = 14
    base["Heading1"].spaceAfter = 8

    base["Heading2"].fontName = "Helvetica-Bold"
    base["Heading2"].fontSize = 12
    base["Heading2"].leading = 15
    base["Heading2"].spaceBefore = 10
    base["Heading2"].spaceAfter = 6

    base["BodyText"].fontName = "Helvetica"
    base["BodyText"].fontSize = 9.5
    base["BodyText"].leading = 13
    base["BodyText"].spaceAfter = 5

    base.add(ParagraphStyle(
        name="Small",
        parent=base["BodyText"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#333333"),
    ))
    base.add(ParagraphStyle(
        name="CodeBlock",
        parent=base["Code"],
        fontName="Courier",
        fontSize=7.2,
        leading=9,
        leftIndent=8,
        rightIndent=8,
        backColor=colors.HexColor("#F4F6F8"),
        borderColor=colors.HexColor("#D9DEE3"),
        borderWidth=0.4,
        borderPadding=6,
    ))
    return base


def p(text, style="BodyText"):
    return Paragraph(text, STYLES[style])


def bullets(items):
    return ListFlowable(
        [ListItem(p(item), leftIndent=12) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
    )


def table(data, widths=None):
    t = Table(data, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2933")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD2D9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def code_block(text):
    return Preformatted(text.strip(), STYLES["CodeBlock"])


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(1.6 * cm, 1.0 * cm, "Proyecto Final SOLID - Sistema Municipal de Turnos")
    canvas.drawRightString(A4[0] - 1.6 * cm, 1.0 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.7 * cm,
        title="Informe Proyecto SOLID - Sistema Municipal de Turnos",
        author="Joaquin Cortez",
    )

    story = []

    story.append(p("Informe de Avance y Documentacion del Proyecto", "Title"))
    story.append(Spacer(1, 0.2 * cm))
    story.append(p("<b>Sistema Municipal de Turnos - Aplicacion del Principio de Sustitucion de Liskov (SOLID)</b>", "Heading2"))
    story.append(p("Fecha del informe: 17/06/2026"))
    story.append(p(f"Repositorio fuente: <a href='{REPO_URL}'>{REPO_URL}</a>"))
    story.append(p("Repositorio remoto local detectado: <b>git@github.com:JoaquinCortezHub/proyecto_final_solid.git</b>"))

    story.append(p("1. Objetivo del informe", "Heading1"))
    story.append(p(
        "El presente informe resume el trabajo desarrollado para el Practico Nro. 3 de Programacion Avanzada, "
        "orientado a demostrar la aplicacion de un principio SOLID en un sistema real. El proyecto implementa "
        "un sistema de turnos municipales por consola, con persistencia en Supabase y separacion de responsabilidades "
        "entre modelo de dominio, menu de interaccion y acceso a datos."
    ))

    story.append(p("2. Consigna tomada como base", "Heading1"))
    story.append(bullets([
        "Aplicar correctamente un principio SOLID asignado por el docente.",
        "Desarrollar un sistema sobre un rubro o industria definida, en este caso gestion municipal de turnos.",
        "Realizar un modelo de base de datos relacional.",
        "Incluir diagrama Entidad-Relacion y flujo funcional.",
        "No es obligatorio contar con GUI, por lo que se implementa una interfaz por terminal.",
        "La evaluacion contempla la explicacion conceptual de los principios SOLID.",
    ]))

    story.append(p("3. Stack tecnologico", "Heading1"))
    story.append(table([
        ["Elemento", "Detalle"],
        ["Lenguaje", "Java"],
        ["IDE previsto", "IntelliJ IDEA"],
        ["Interfaz", "Menu por terminal con Scanner"],
        ["Base de datos", "Supabase sobre PostgreSQL"],
        ["Integracion", "Supabase REST API usando java.net.http.HttpClient"],
        ["Persistencia", "Tablas ciudadanos, servicios, turnos y pagos"],
        ["Repositorio", REPO_URL],
    ], [5 * cm, 11 * cm]))

    story.append(p("4. Descripcion general del sistema", "Heading1"))
    story.append(p(
        "El sistema permite que un ciudadano solicite turnos municipales y luego consulte sus turnos por DNI. "
        "Actualmente soporta dos tipos principales: licencia de conducir, que es un turno arancelado, y asistencia "
        "social alimentaria, que es un turno gratuito. El sistema tambien permite pagar turnos arancelados mediante "
        "la seleccion del ID del turno; en el flujo actual de demo, pagar implica eliminar el turno de Supabase."
    ))

    story.append(p("Funcionalidades implementadas", "Heading2"))
    story.append(bullets([
        "Menu principal con opciones: Sacar turno, Ver mis turnos, Pagar turno arancelado y Salir.",
        "Submenu para elegir entre licencia de conducir y asistencia social alimentaria.",
        "Asignacion automatica de fecha y hora: licencia a 7 dias a las 09:00, social a 3 dias a las 10:30.",
        "Reutilizacion de ciudadano existente por DNI para no pedir datos personales repetidos.",
        "Alta de ciudadano si el DNI no existe.",
        "Alta de turno asociado a ciudadano y servicio.",
        "Alta automatica de pago para servicios arancelados.",
        "Consulta formateada de turnos por DNI.",
        "Pago/eliminacion de turno arancelado por ID.",
    ]))

    story.append(p("5. Aplicacion del Principio de Sustitucion de Liskov", "Heading1"))
    story.append(p(
        "El principio de sustitucion de Liskov establece que una clase derivada debe poder reemplazar a su tipo base "
        "sin alterar el comportamiento correcto del programa. En este proyecto, el tipo base es la interfaz "
        "<b>TurnoMunicipal</b>. Tanto <b>TurnoSocial</b> como <b>TurnoLicencia</b> pueden usarse donde el sistema espera "
        "un TurnoMunicipal, porque ambos cumplen el contrato minimo: obtener detalle, obtener fecha/hora y confirmar turno."
    ))
    story.append(code_block("""
public interface TurnoMunicipal {
    String getDetalleTurno();
    String getFechaHora();
    void confirmarTurno();
}

public interface TurnoArancelado extends TurnoMunicipal {
    double calcularCosto();
    void generarBoletoPago();
}
"""))
    story.append(p(
        "El diseno evita forzar a todos los turnos a tener comportamiento de pago. Un turno social no deberia calcular "
        "costos ni generar boleto, por lo tanto no implementa TurnoArancelado. En cambio, TurnoLicencia si lo hace. "
        "Esto mantiene el contrato coherente y evita errores como UnsupportedOperationException en tipos que no deberian pagar."
    ))

    story.append(p("Instanciacion real en el menu", "Heading2"))
    story.append(code_block("""
TurnoMunicipal turno;

if (opcion == 1) {
    turno = new TurnoLicencia(fechaHora, "B1");
} else {
    turno = new TurnoSocial(fechaHora, "Asistencia alimentaria");
}

supabaseClient.registrarTurno(
    dni, nombreCompleto, email, telefono, servicio, turno.getFechaHora()
);
"""))

    story.append(p("6. Estructura del codigo fuente", "Heading1"))
    story.append(table([
        ["Archivo", "Responsabilidad"],
        ["Main.java", "Controla el menu de terminal, lee opciones, instancia turnos y llama a SupabaseClient."],
        ["TurnoMunicipal.java", "Contrato base para cualquier turno municipal."],
        ["TurnoArancelado.java", "Contrato especifico para turnos que tienen costo y boleto de pago."],
        ["TurnoSocial.java", "Implementacion de turno gratuito."],
        ["TurnoLicencia.java", "Implementacion de turno arancelado para licencia de conducir."],
        ["ProcesadorTurnos.java", "Servicio de apoyo para reportes y procesamiento conceptual de pagos."],
        ["SupabaseClient.java", "Capa de acceso a datos: consultas REST, altas, eliminaciones y parseo de respuestas."],
    ], [5 * cm, 11 * cm]))

    story.append(p("7. Flujo funcional principal", "Heading1"))
    story.append(p("Flujo para sacar un turno:"))
    story.append(bullets([
        "El usuario selecciona Sacar turno.",
        "Elige tipo de turno: licencia de conducir o asistencia social alimentaria.",
        "El sistema asigna fecha y hora automaticamente.",
        "El sistema instancia TurnoLicencia o TurnoSocial como TurnoMunicipal.",
        "El usuario ingresa DNI.",
        "SupabaseClient consulta si el ciudadano ya existe.",
        "Si existe, se reutilizan sus datos; si no existe, se solicitan nombre, email y telefono.",
        "Se busca o crea el servicio en Supabase.",
        "Se crea el turno en la tabla turnos.",
        "Si el servicio es arancelado, se crea un registro en pagos.",
    ]))
    story.append(p("Flujo para ver turnos:"))
    story.append(bullets([
        "El usuario ingresa su DNI.",
        "SupabaseClient consulta turnos, servicios, pagos y ciudadano mediante relaciones REST.",
        "El menu muestra cada turno con ID, servicio, fecha, estado, tipo y datos de pago si corresponde.",
    ]))
    story.append(p("Flujo para pagar un turno arancelado:"))
    story.append(bullets([
        "El usuario ingresa su DNI.",
        "Se listan solo los turnos arancelados.",
        "El usuario ingresa el ID del turno.",
        "El sistema valida que el turno exista y sea arancelado.",
        "El turno se elimina de Supabase. El pago asociado se elimina por ON DELETE CASCADE.",
    ]))

    story.append(p("8. Modelo de base de datos", "Heading1"))
    story.append(table([
        ["Tabla", "Campos principales", "Descripcion"],
        ["ciudadanos", "id_ciudadano, dni, nombre_completo, email, telefono", "Personas que solicitan turnos."],
        ["servicios", "id_servicio, nombre_servicio, es_arancelado, costo_base", "Catalogo de servicios municipales."],
        ["turnos", "id_turno, id_ciudadano, id_servicio, fecha_hora, estado", "Registro principal de turnos."],
        ["pagos", "id_pago, id_turno, monto_final, fecha_pago, estado_pago", "Pago asociado a turnos arancelados."],
    ], [3.2 * cm, 6.2 * cm, 6.6 * cm]))
    story.append(p("Relaciones:"))
    story.append(bullets([
        "Un ciudadano puede tener muchos turnos: ciudadanos 1:N turnos.",
        "Un servicio puede estar asociado a muchos turnos: servicios 1:N turnos.",
        "Un turno arancelado puede generar un pago: turnos 1:0..1 pagos.",
        "La tabla pagos depende de turnos mediante id_turno con eliminacion en cascada.",
    ]))

    if DER_IMAGE.exists():
        story.append(PageBreak())
        story.append(p("9. Diagrama Entidad-Relacion", "Heading1"))
        story.append(p("Captura/diagrama incluido como evidencia visual del modelo relacional implementado en Supabase."))
        img = Image(str(DER_IMAGE))
        max_w = 17 * cm
        max_h = 11 * cm
        scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        story.append(img)

    story.append(PageBreak())
    story.append(p("10. Integracion con Supabase", "Heading1"))
    story.append(p(
        "La integracion se realiza mediante la API REST de Supabase. La clase SupabaseClient construye peticiones HTTP "
        "con HttpClient y maneja metodos GET, POST y DELETE. Para la demo local se uso una credencial de servicio en el "
        "codigo fuente; por seguridad, en este informe no se reproduce la clave completa. En una version productiva deberia "
        "moverse a variables de entorno y no subirse a GitHub."
    ))
    story.append(table([
        ["Operacion", "Endpoint REST", "Uso"],
        ["Buscar ciudadano", "/ciudadanos?select=...&dni=eq.{dni}&limit=1", "Evita duplicar personas."],
        ["Crear ciudadano", "POST /ciudadanos", "Alta si el DNI no existe."],
        ["Buscar servicio", "/servicios?select=...&nombre_servicio=eq.{nombre}", "Obtiene ID y costo."],
        ["Crear servicio", "POST /servicios", "Respaldo si la tabla servicios esta vacia."],
        ["Crear turno", "POST /turnos", "Registra la solicitud del ciudadano."],
        ["Crear pago", "POST /pagos", "Se ejecuta solo para turnos arancelados."],
        ["Listar turnos", "/turnos?select=...,servicios(...),pagos(...),ciudadanos!inner(dni)", "Consulta formateada por DNI."],
        ["Pagar/eliminar", "DELETE /turnos?id_turno=eq.{id}", "Elimina el turno arancelado seleccionado."],
    ], [3.2 * cm, 7.6 * cm, 5.2 * cm]))

    story.append(p("12. Estado actual y pendientes", "Heading1"))
    story.append(table([
        ["Area", "Estado"],
        ["Modelo SOLID/LSP", "Implementado y demostrable con TurnoMunicipal, TurnoSocial, TurnoLicencia y TurnoArancelado."],
        ["Menu terminal", "Implementado con altas, consultas y pago/eliminacion de turnos arancelados."],
        ["Supabase", "Integrado por REST API con tablas relacionales."],
        ["DER", "Incluido como imagen en este informe."],
        ["Seguridad", "Pendiente: mover SERVICE_ROLE_KEY a variable de entorno antes de publicar o entregar repositorio publico."],
        ["Videos/capturas extra", "Pendiente si se desea agregar grabacion de ejecucion."],
    ], [4 * cm, 12 * cm]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


STYLES = styles()


if __name__ == "__main__":
    build()
