package com.municipio.turnos.modelos;

import com.municipio.turnos.interfaces.TurnoMunicipal;

public class TurnoSocial implements TurnoMunicipal {
    private String fechaHora;
    private String motivo;

    public TurnoSocial(String fechaHora, String motivo) {
        this.fechaHora = fechaHora;
        this.motivo = motivo;
    }

    @Override
    public String getDetalleTurno() {
        return "Turno Social (Gratuito) - Motivo: " + motivo;
    }

    @Override
    public String getFechaHora() {
        return this.fechaHora;
    }

    @Override
    public void confirmarTurno() {
        System.out.println("Turno social confirmado para el " + fechaHora);
    }
}