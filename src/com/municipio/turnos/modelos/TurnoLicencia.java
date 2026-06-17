package com.municipio.turnos.modelos;

import com.municipio.turnos.interfaces.TurnoArancelado;

public class TurnoLicencia implements TurnoArancelado {
    private String fechaHora;
    private String categoriaLicencia;

    public TurnoLicencia(String fechaHora, String categoriaLicencia) {
        this.fechaHora = fechaHora;
        this.categoriaLicencia = categoriaLicencia;
    }

    @Override
    public String getDetalleTurno() {
        return "Renovación Licencia Categ. " + categoriaLicencia;
    }

    @Override
    public String getFechaHora() {
        return this.fechaHora;
    }

    @Override
    public void confirmarTurno() {
        System.out.println("Turno de licencia confirmado. Pendiente de pago.");
    }

    @Override
    public double calcularCosto() {
        // Lógica simplificada de costos
        return categoriaLicencia.equals("B1") ? 15000.0 : 20000.0;
    }

    @Override
    public void generarBoletoPago() {
        System.out.println("Generando boleto por $" + calcularCosto() + " para el turno de Licencia.");
    }
}