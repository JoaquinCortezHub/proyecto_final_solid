package com.municipio.turnos.servicios;

import com.municipio.turnos.interfaces.TurnoArancelado;
import com.municipio.turnos.interfaces.TurnoMunicipal;
import com.municipio.turnos.modelos.TurnoLicencia;
import com.municipio.turnos.modelos.TurnoSocial;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class GestorTurnos {
    public static final String SERVICIO_LICENCIA = "Licencia de conducir";
    public static final String SERVICIO_SOCIAL = "Asistencia social alimentaria";
    public static final double PORCENTAJE_DESCUENTO_MAYOR_65 = 0.30;

    private static final DateTimeFormatter FORMATO_SUPABASE = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final SupabaseClient supabaseClient;

    public GestorTurnos(SupabaseClient supabaseClient) {
        this.supabaseClient = supabaseClient;
    }

    public ResultadoTurno sacarTurno(SolicitudTurno solicitud) throws IOException, InterruptedException {
        TurnoMunicipal turno = crearTurnoMunicipal(solicitud.servicio());
        double montoOriginal = calcularMontoOriginal(turno);
        double descuento = calcularDescuento(turno, solicitud.mayor65(), montoOriginal);
        double montoFinal = montoOriginal - descuento;

        int idTurno = supabaseClient.registrarTurno(
                solicitud.dni(),
                solicitud.nombreCompleto(),
                solicitud.email(),
                solicitud.telefono(),
                solicitud.mayor65(),
                solicitud.servicio(),
                turno.getFechaHora(),
                montoOriginal,
                descuento,
                montoFinal
        );

        return new ResultadoTurno(
                idTurno,
                turno.getDetalleTurno(),
                turno.getFechaHora(),
                turno instanceof TurnoArancelado,
                montoOriginal,
                descuento,
                montoFinal
        );
    }

    public List<SupabaseClient.TurnoDetalle> obtenerTurnosPorDni(String dni) throws IOException, InterruptedException {
        return supabaseClient.obtenerTurnosPorDni(dni);
    }

    public SupabaseClient.Ciudadano buscarCiudadanoPorDni(String dni) throws IOException, InterruptedException {
        return supabaseClient.buscarCiudadanoPorDni(dni);
    }

    public void pagarTurnoArancelado(String dni, int idTurno) throws IOException, InterruptedException {
        supabaseClient.pagarTurnoArancelado(dni, idTurno);
    }

    public void cancelarTurno(String dni, int idTurno) throws IOException, InterruptedException {
        supabaseClient.cancelarTurno(dni, idTurno);
    }

    public List<String> obtenerServiciosDisponibles() {
        return List.of(SERVICIO_LICENCIA, SERVICIO_SOCIAL);
    }

    private TurnoMunicipal crearTurnoMunicipal(String servicio) throws IOException {
        String fechaHora = asignarFechaHoraTurno(servicio);

        if (SERVICIO_LICENCIA.equals(servicio)) {
            return new TurnoLicencia(fechaHora, "B1");
        }

        if (SERVICIO_SOCIAL.equals(servicio)) {
            return new TurnoSocial(fechaHora, "Asistencia alimentaria");
        }

        throw new IOException("Servicio no reconocido: " + servicio);
    }

    private String asignarFechaHoraTurno(String servicio) {
        LocalDate fechaBase = LocalDate.now();

        if (SERVICIO_LICENCIA.equals(servicio)) {
            return LocalDateTime.of(fechaBase.plusDays(7), LocalTime.of(9, 0)).format(FORMATO_SUPABASE);
        }

        return LocalDateTime.of(fechaBase.plusDays(3), LocalTime.of(10, 30)).format(FORMATO_SUPABASE);
    }

    private double calcularMontoOriginal(TurnoMunicipal turno) {
        if (turno instanceof TurnoArancelado turnoArancelado) {
            return turnoArancelado.calcularCosto();
        }

        return 0.0;
    }

    private double calcularDescuento(TurnoMunicipal turno, boolean mayor65, double montoOriginal) {
        if (mayor65 && turno instanceof TurnoArancelado) {
            return montoOriginal * PORCENTAJE_DESCUENTO_MAYOR_65;
        }

        return 0.0;
    }
}
