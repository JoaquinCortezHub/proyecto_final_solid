package com.municipio.turnos.servicios;

public record SolicitudTurno(
        String dni,
        String nombreCompleto,
        String email,
        String telefono,
        boolean mayor65,
        String servicio
) {
}
