package com.municipio.turnos.interfaces;

public interface TurnoArancelado extends TurnoMunicipal {
    double calcularCosto();
    void generarBoletoPago();
}