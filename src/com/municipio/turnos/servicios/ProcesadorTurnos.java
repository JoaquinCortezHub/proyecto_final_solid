package com.municipio.turnos.servicios;

import com.municipio.turnos.interfaces.TurnoArancelado;
import com.municipio.turnos.interfaces.TurnoMunicipal;
import java.util.List;

public class ProcesadorTurnos {

    public void imprimirReporteTurnos(List<TurnoMunicipal> turnos) {
        System.out.println("--- REPORTE DE TURNOS DEL DÍA ---");
        for (TurnoMunicipal turno : turnos) {
            System.out.println(turno.getDetalleTurno() + " | Fecha: " + turno.getFechaHora());
            turno.confirmarTurno();
        }
    }

    public void procesarPagos(List<TurnoArancelado> turnosArancelados) {
        System.out.println("--- PROCESANDO PAGOS ---");
        for (TurnoArancelado turno : turnosArancelados) {
            turno.generarBoletoPago();
        }
    }
}