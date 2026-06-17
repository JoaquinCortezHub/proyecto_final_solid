package com.municipio.turnos.servicios;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SupabaseClient {
    private static final String REST_URL = readRequiredEnv("SUPABASE_URL") + "/rest/v1";
    private static final String SERVICE_ROLE_KEY = readRequiredEnv("SUPABASE_SERVICE_ROLE_KEY");
    private static final String SERVICIO_LICENCIA = "Licencia de conducir";
    private static final String SERVICIO_SOCIAL = "Asistencia social alimentaria";

    private final HttpClient httpClient;

    public SupabaseClient() {
        this.httpClient = HttpClient.newHttpClient();
    }

    private static String readRequiredEnv(String name) {
        String value = System.getenv(name);

        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Falta configurar la variable de entorno " + name);
        }

        return value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
    }

    public void registrarTurno(
            String dni,
            String nombreCompleto,
            String email,
            String telefono,
            String servicio,
            String fechaHora
    ) throws IOException, InterruptedException {
        int ciudadanoId = buscarOCrearCiudadano(dni, nombreCompleto, email, telefono);
        ServicioMunicipal servicioMunicipal = buscarServicio(servicio);
        int turnoId = crearTurno(dni, ciudadanoId, servicioMunicipal.idServicio(), fechaHora);

        if (servicioMunicipal.esArancelado()) {
            crearPago(dni, turnoId, servicioMunicipal.costoBase());
        }
    }

    public List<TurnoDetalle> obtenerTurnosPorDni(String dni) throws IOException, InterruptedException {
        String select = "id_turno,fecha_hora,estado,servicios(nombre_servicio,es_arancelado,costo_base),pagos(monto_final,estado_pago),ciudadanos!inner(dni)";
        String path = "/turnos?select=" + encode(select)
                + "&ciudadanos.dni=eq." + encode(dni)
                + "&order=fecha_hora.desc";

        String response = get(path, dni);
        List<TurnoDetalle> turnos = new ArrayList<>();

        for (String objectJson : extractObjects(response)) {
            turnos.add(new TurnoDetalle(
                    extractInt(objectJson, "id_turno"),
                    extractString(objectJson, "fecha_hora"),
                    extractString(objectJson, "estado"),
                    extractString(objectJson, "nombre_servicio"),
                    extractBoolean(objectJson, "es_arancelado"),
                    extractDouble(objectJson, "costo_base"),
                    extractNullableDouble(objectJson, "monto_final"),
                    extractNullableString(objectJson, "estado_pago")
            ));
        }

        return turnos;
    }

    public Ciudadano buscarCiudadanoPorDni(String dni) throws IOException, InterruptedException {
        String response = get("/ciudadanos?select=id_ciudadano,dni,nombre_completo,email,telefono&dni=eq."
                + encode(dni) + "&limit=1", dni);
        Integer idCiudadano = extractNullableInt(response, "id_ciudadano");

        if (idCiudadano == null) {
            return null;
        }

        return new Ciudadano(
                idCiudadano,
                extractString(response, "dni"),
                extractString(response, "nombre_completo"),
                extractNullableString(response, "email"),
                extractNullableString(response, "telefono")
        );
    }

    public void pagarTurnoArancelado(String dni, int idTurno) throws IOException, InterruptedException {
        List<TurnoDetalle> turnos = obtenerTurnosPorDni(dni);
        TurnoDetalle turnoSeleccionado = null;

        for (TurnoDetalle turno : turnos) {
            if (turno.idTurno() == idTurno) {
                turnoSeleccionado = turno;
                break;
            }
        }

        if (turnoSeleccionado == null) {
            throw new IOException("No existe un turno con ese ID para el DNI ingresado.");
        }

        if (!turnoSeleccionado.esArancelado()) {
            throw new IOException("El turno seleccionado no es arancelado.");
        }

        delete("/turnos?id_turno=eq." + idTurno, dni);
    }

    private int buscarOCrearCiudadano(
            String dni,
            String nombreCompleto,
            String email,
            String telefono
    ) throws IOException, InterruptedException {
        String response = get("/ciudadanos?select=id_ciudadano&dni=eq." + encode(dni) + "&limit=1", dni);
        Integer idExistente = extractNullableInt(response, "id_ciudadano");

        if (idExistente != null) {
            return idExistente;
        }

        String body = "{"
                + "\"dni\":\"" + escapeJson(dni) + "\","
                + "\"nombre_completo\":\"" + escapeJson(nombreCompleto) + "\","
                + "\"email\":\"" + escapeJson(email) + "\","
                + "\"telefono\":\"" + escapeJson(telefono) + "\""
                + "}";

        String createResponse = post("/ciudadanos", body, dni);
        return extractInt(createResponse, "id_ciudadano");
    }

    private ServicioMunicipal buscarServicio(String nombreServicio) throws IOException, InterruptedException {
        String response = get("/servicios?select=id_servicio,nombre_servicio,es_arancelado,costo_base&nombre_servicio=eq."
                + encode(nombreServicio) + "&limit=1");

        if (extractNullableInt(response, "id_servicio") == null) {
            return crearServicio(nombreServicio);
        }

        return new ServicioMunicipal(
                extractInt(response, "id_servicio"),
                extractString(response, "nombre_servicio"),
                extractBoolean(response, "es_arancelado"),
                extractDouble(response, "costo_base")
        );
    }

    private ServicioMunicipal crearServicio(String nombreServicio) throws IOException, InterruptedException {
        boolean esArancelado = SERVICIO_LICENCIA.equals(nombreServicio);
        double costoBase = esArancelado ? 15000.0 : 0.0;

        if (!SERVICIO_LICENCIA.equals(nombreServicio) && !SERVICIO_SOCIAL.equals(nombreServicio)) {
            throw new IOException("Servicio no reconocido: " + nombreServicio);
        }

        String body = "{"
                + "\"nombre_servicio\":\"" + escapeJson(nombreServicio) + "\","
                + "\"es_arancelado\":" + esArancelado + ","
                + "\"costo_base\":" + costoBase
                + "}";

        String response = post("/servicios", body, null);

        return new ServicioMunicipal(
                extractInt(response, "id_servicio"),
                extractString(response, "nombre_servicio"),
                extractBoolean(response, "es_arancelado"),
                extractDouble(response, "costo_base")
        );
    }

    private int crearTurno(String dni, int ciudadanoId, int servicioId, String fechaHora) throws IOException, InterruptedException {
        String body = "{"
                + "\"id_ciudadano\":" + ciudadanoId + ","
                + "\"id_servicio\":" + servicioId + ","
                + "\"fecha_hora\":\"" + escapeJson(fechaHora) + "\","
                + "\"estado\":\"Pendiente\""
                + "}";

        String response = post("/turnos", body, dni);
        return extractInt(response, "id_turno");
    }

    private void crearPago(String dni, int turnoId, double montoFinal) throws IOException, InterruptedException {
        String body = "{"
                + "\"id_turno\":" + turnoId + ","
                + "\"monto_final\":" + montoFinal + ","
                + "\"estado_pago\":\"Pendiente\""
                + "}";

        post("/pagos", body, dni);
    }

    private String get(String path) throws IOException, InterruptedException {
        HttpRequest request = requestBuilder(path, null).GET().build();
        return send(request);
    }

    private String get(String path, String dni) throws IOException, InterruptedException {
        HttpRequest request = requestBuilder(path, dni).GET().build();
        return send(request);
    }

    private String post(String path, String body, String dni) throws IOException, InterruptedException {
        HttpRequest request = requestBuilder(path, dni)
                .header("Content-Type", "application/json")
                .header("Prefer", "return=representation")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        return send(request);
    }

    private String delete(String path, String dni) throws IOException, InterruptedException {
        HttpRequest request = requestBuilder(path, dni)
                .header("Prefer", "return=representation")
                .DELETE()
                .build();

        return send(request);
    }

    private HttpRequest.Builder requestBuilder(String path, String dni) {
        HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(REST_URL + path))
                .header("apikey", SERVICE_ROLE_KEY);

        if (SERVICE_ROLE_KEY.startsWith("eyJ")) {
            builder.header("Authorization", "Bearer " + SERVICE_ROLE_KEY);
        }

        if (dni != null && !dni.isBlank()) {
            builder.header("x-dni", dni);
        }

        return builder;
    }

    private String send(HttpRequest request) throws IOException, InterruptedException {
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        int statusCode = response.statusCode();

        if (statusCode < 200 || statusCode >= 300) {
            throw new IOException("Supabase respondio HTTP " + statusCode + ": " + response.body());
        }

        return response.body();
    }

    private static String encode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8).replace("+", "%20");
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static List<String> extractObjects(String jsonArray) {
        List<String> objects = new ArrayList<>();
        int depth = 0;
        int start = -1;

        for (int i = 0; i < jsonArray.length(); i++) {
            char current = jsonArray.charAt(i);
            if (current == '{') {
                if (depth == 0) {
                    start = i;
                }
                depth++;
            } else if (current == '}') {
                depth--;
                if (depth == 0 && start >= 0) {
                    objects.add(jsonArray.substring(start, i + 1));
                    start = -1;
                }
            }
        }

        return objects;
    }

    private static int extractInt(String json, String field) {
        Integer value = extractNullableInt(json, field);
        if (value == null) {
            throw new IllegalArgumentException("No se encontro el campo numerico " + field + " en la respuesta.");
        }

        return value;
    }

    private static Integer extractNullableInt(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(\\d+)").matcher(json);
        return matcher.find() ? Integer.parseInt(matcher.group(1)) : null;
    }

    private static String extractString(String json, String field) {
        String value = extractNullableString(json, field);
        if (value == null) {
            throw new IllegalArgumentException("No se encontro el campo de texto " + field + " en la respuesta.");
        }

        return value;
    }

    private static String extractNullableString(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*\"([^\"]*)\"").matcher(json);
        return matcher.find() ? matcher.group(1) : null;
    }

    private static boolean extractBoolean(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(true|false)").matcher(json);
        if (!matcher.find()) {
            throw new IllegalArgumentException("No se encontro el campo booleano " + field + " en la respuesta.");
        }

        return Boolean.parseBoolean(matcher.group(1));
    }

    private static double extractDouble(String json, String field) {
        Double value = extractNullableDouble(json, field);
        if (value == null) {
            throw new IllegalArgumentException("No se encontro el campo decimal " + field + " en la respuesta.");
        }

        return value;
    }

    private static Double extractNullableDouble(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(\\d+(?:\\.\\d+)?)").matcher(json);
        return matcher.find() ? Double.parseDouble(matcher.group(1)) : null;
    }

    private record ServicioMunicipal(int idServicio, String nombreServicio, boolean esArancelado, double costoBase) {
    }

    public record TurnoDetalle(
            int idTurno,
            String fechaHora,
            String estado,
            String nombreServicio,
            boolean esArancelado,
            double costoBase,
            Double montoFinal,
            String estadoPago
    ) {
    }

    public record Ciudadano(
            int idCiudadano,
            String dni,
            String nombreCompleto,
            String email,
            String telefono
    ) {
    }
}
