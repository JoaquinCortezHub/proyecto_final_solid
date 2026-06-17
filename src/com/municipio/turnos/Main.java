package com.municipio.turnos;

import com.municipio.turnos.interfaces.TurnoMunicipal;
import com.municipio.turnos.modelos.TurnoLicencia;
import com.municipio.turnos.modelos.TurnoSocial;
import com.municipio.turnos.servicios.SupabaseClient;
import com.municipio.turnos.servicios.SupabaseClient.Ciudadano;
import com.municipio.turnos.servicios.SupabaseClient.TurnoDetalle;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.InputMismatchException;
import java.util.List;
import java.util.Scanner;

public class Main {
    private static final String SERVICIO_LICENCIA = "Licencia de conducir";
    private static final String SERVICIO_SOCIAL = "Asistencia social alimentaria";
    private static final DateTimeFormatter FORMATO_SUPABASE = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) {
        SupabaseClient supabaseClient = new SupabaseClient();
        Scanner scanner = new Scanner(System.in);

        boolean salir = false;
        while (!salir) {
            imprimirMenuPrincipal();
            int opcion = leerOpcion(scanner);

            switch (opcion) {
                case 1:
                    sacarTurno(scanner, supabaseClient);
                    break;
                case 2:
                    verMisTurnos(scanner, supabaseClient);
                    break;
                case 3:
                    pagarTurnoArancelado(scanner, supabaseClient);
                    break;
                case 0:
                    salir = true;
                    System.out.println("Sistema finalizado.");
                    break;
                default:
                    System.out.println("Opcion invalida. Intente nuevamente.");
                    break;
            }

            System.out.println();
        }

        scanner.close();
    }

    private static void imprimirMenuPrincipal() {
        System.out.println("=== Sistema Municipal de Turnos ===");
        System.out.println("1. Sacar turno");
        System.out.println("2. Ver mis turnos");
        System.out.println("3. Pagar turno arancelado");
        System.out.println("0. Salir");
        System.out.print("Seleccione una opcion: ");
    }

    private static void imprimirMenuTurnos() {
        System.out.println("--- Sacar turno ---");
        System.out.println("1. Licencia de conducir (arancelado)");
        System.out.println("2. Asistencia social alimentaria (gratuito)");
        System.out.println("0. Volver");
        System.out.print("Seleccione el tipo de turno: ");
    }

    private static int leerOpcion(Scanner scanner) {
        try {
            int opcion = scanner.nextInt();
            scanner.nextLine();
            return opcion;
        } catch (InputMismatchException e) {
            scanner.nextLine();
            return -1;
        }
    }

    private static void sacarTurno(Scanner scanner, SupabaseClient supabaseClient) {
        imprimirMenuTurnos();
        int opcion = leerOpcion(scanner);

        String servicio;
        TurnoMunicipal turno;
        String fechaHora;

        switch (opcion) {
            case 1:
                servicio = SERVICIO_LICENCIA;
                fechaHora = asignarFechaHoraTurno(servicio);
                turno = new TurnoLicencia(fechaHora, "B1");
                break;
            case 2:
                servicio = SERVICIO_SOCIAL;
                fechaHora = asignarFechaHoraTurno(servicio);
                turno = new TurnoSocial(fechaHora, "Asistencia alimentaria");
                break;
            case 0:
                return;
            default:
                System.out.println("Tipo de turno invalido.");
                return;
        }

        System.out.println();
        System.out.println("--- Datos del ciudadano ---");
        System.out.print("DNI: ");
        String dni = scanner.nextLine();

        String nombreCompleto;
        String email;
        String telefono;

        try {
            Ciudadano ciudadano = supabaseClient.buscarCiudadanoPorDni(dni);
            if (ciudadano != null) {
                nombreCompleto = ciudadano.nombreCompleto();
                email = ciudadano.email() != null ? ciudadano.email() : "";
                telefono = ciudadano.telefono() != null ? ciudadano.telefono() : "";
                System.out.println("Ciudadano encontrado: " + nombreCompleto);
            } else {
                System.out.print("Nombre completo: ");
                nombreCompleto = scanner.nextLine();
                System.out.print("Email: ");
                email = scanner.nextLine();
                System.out.print("Telefono: ");
                telefono = scanner.nextLine();
            }
        } catch (IOException e) {
            System.out.println("No se pudo consultar el ciudadano en Supabase.");
            System.out.println("Detalle: " + e.getMessage());
            return;
        } catch (InterruptedException e) {
            System.out.println("La operacion fue interrumpida.");
            Thread.currentThread().interrupt();
            return;
        }

        try {
            supabaseClient.registrarTurno(dni, nombreCompleto, email, telefono, servicio, turno.getFechaHora());
            System.out.println();
            System.out.println("Turno guardado correctamente en Supabase.");
            System.out.println("Detalle: " + turno.getDetalleTurno());
            System.out.println("Fecha y hora: " + turno.getFechaHora());
            turno.confirmarTurno();
        } catch (IOException e) {
            System.out.println("No se pudo guardar el turno en Supabase.");
            System.out.println("Detalle: " + e.getMessage());
        } catch (InterruptedException e) {
            System.out.println("La operacion fue interrumpida.");
            Thread.currentThread().interrupt();
        }
    }

    private static void pagarTurnoArancelado(Scanner scanner, SupabaseClient supabaseClient) {
        System.out.print("Ingrese su DNI: ");
        String dni = scanner.nextLine();

        try {
            List<TurnoDetalle> turnos = supabaseClient.obtenerTurnosPorDni(dni);
            List<TurnoDetalle> turnosArancelados = turnos.stream()
                    .filter(TurnoDetalle::esArancelado)
                    .toList();

            if (turnosArancelados.isEmpty()) {
                System.out.println("No hay turnos arancelados para pagar.");
                return;
            }

            System.out.println();
            System.out.println("=== Turnos arancelados pendientes ===");
            imprimirTurnos(turnosArancelados);
            System.out.print("Ingrese el ID del turno a pagar: ");
            int idTurno = leerOpcion(scanner);

            supabaseClient.pagarTurnoArancelado(dni, idTurno);
            System.out.println("Pago registrado. El turno arancelado fue eliminado de Supabase.");
        } catch (IOException e) {
            System.out.println("No se pudo pagar el turno.");
            System.out.println("Detalle: " + e.getMessage());
        } catch (InterruptedException e) {
            System.out.println("La operacion fue interrumpida.");
            Thread.currentThread().interrupt();
        }
    }

    private static String asignarFechaHoraTurno(String servicio) {
        LocalDate fechaBase = LocalDate.now();

        if (SERVICIO_LICENCIA.equals(servicio)) {
            return LocalDateTime.of(fechaBase.plusDays(7), LocalTime.of(9, 0)).format(FORMATO_SUPABASE);
        }

        return LocalDateTime.of(fechaBase.plusDays(3), LocalTime.of(10, 30)).format(FORMATO_SUPABASE);
    }

    private static void verMisTurnos(Scanner scanner, SupabaseClient supabaseClient) {
        System.out.print("Ingrese su DNI: ");
        String dni = scanner.nextLine();

        try {
            List<TurnoDetalle> turnos = supabaseClient.obtenerTurnosPorDni(dni);
            imprimirTurnos(turnos);
        } catch (IOException e) {
            System.out.println("No se pudieron obtener los turnos desde Supabase.");
            System.out.println("Detalle: " + e.getMessage());
        } catch (InterruptedException e) {
            System.out.println("La operacion fue interrumpida.");
            Thread.currentThread().interrupt();
        }
    }

    private static void imprimirTurnos(List<TurnoDetalle> turnos) {
        if (turnos.isEmpty()) {
            System.out.println("No se encontraron turnos para el DNI ingresado.");
            return;
        }

        System.out.println();
        System.out.println("=== Mis turnos ===");
        for (TurnoDetalle turno : turnos) {
            System.out.println("----------------------------------------");
            System.out.println("Turno Nro.: " + turno.idTurno());
            System.out.println("Servicio: " + turno.nombreServicio());
            System.out.println("Fecha y hora: " + turno.fechaHora());
            System.out.println("Estado: " + turno.estado());

            if (turno.esArancelado()) {
                double monto = turno.montoFinal() != null ? turno.montoFinal() : turno.costoBase();
                String estadoPago = turno.estadoPago() != null ? turno.estadoPago() : "Pendiente";
                System.out.println("Tipo: Arancelado");
                System.out.println("Monto: $" + monto);
                System.out.println("Estado del pago: " + estadoPago);
            } else {
                System.out.println("Tipo: Gratuito");
            }
        }
        System.out.println("----------------------------------------");
    }
}
