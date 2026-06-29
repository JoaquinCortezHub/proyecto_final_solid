package com.municipio.turnos.servicios.records;

public record ResultadoTurno(
        int idTurno,
        String detalle,
        String fechaHora,
        boolean arancelado,
        double montoOriginal,
        double descuentoAplicado,
        double montoFinal
) {
}
