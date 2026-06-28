package com.municipio.turnos.ui;

import com.municipio.turnos.servicios.GestorTurnos;
import com.municipio.turnos.servicios.ResultadoTurno;
import com.municipio.turnos.servicios.SolicitudTurno;
import com.municipio.turnos.servicios.SupabaseClient;
import com.municipio.turnos.servicios.SupabaseClient.Ciudadano;
import com.municipio.turnos.servicios.SupabaseClient.TurnoDetalle;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.table.DefaultTableModel;
import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.util.List;

public class SistemaTurnosFrame extends JFrame {
    private final GestorTurnos gestorTurnos;

    private final JTextField dniAltaField = new JTextField(16);
    private final JTextField nombreField = new JTextField(24);
    private final JTextField emailField = new JTextField(24);
    private final JTextField telefonoField = new JTextField(16);
    private final JCheckBox mayor65Check = new JCheckBox("Mayor de 65 anos");
    private final JComboBox<String> servicioCombo = new JComboBox<>();
    private final JTextArea salidaAltaArea = new JTextArea(8, 60);

    private final JTextField dniConsultaField = new JTextField(16);
    private final DefaultTableModel turnosTableModel = new DefaultTableModel(
            new Object[]{
                    "ID", "Servicio", "Fecha", "Estado", "Tipo", "Mayor 65",
                    "Monto original", "Descuento", "Monto final", "Estado pago"
            },
            0
    ) {
        @Override
        public boolean isCellEditable(int row, int column) {
            return false;
        }
    };
    private final JTable turnosTable = new JTable(turnosTableModel);
    private final JTextArea salidaConsultaArea = new JTextArea(5, 60);

    public SistemaTurnosFrame(GestorTurnos gestorTurnos) {
        super("Sistema Municipal de Turnos");
        this.gestorTurnos = gestorTurnos;

        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(980, 640);
        setLocationRelativeTo(null);

        configurarComponentes();
        setContentPane(crearContenido());
    }

    private void configurarComponentes() {
        for (String servicio : gestorTurnos.obtenerServiciosDisponibles()) {
            servicioCombo.addItem(servicio);
        }

        salidaAltaArea.setEditable(false);
        salidaConsultaArea.setEditable(false);
        turnosTable.setAutoCreateRowSorter(true);
    }

    private JTabbedPane crearContenido() {
        JTabbedPane tabs = new JTabbedPane();
        tabs.addTab("Sacar turno", crearPanelAlta());
        tabs.addTab("Mis turnos", crearPanelConsulta());
        tabs.addTab("Servicios", crearPanelServicios());
        return tabs;
    }

    private JPanel crearPanelAlta() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        JPanel form = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.anchor = GridBagConstraints.WEST;
        gbc.fill = GridBagConstraints.HORIZONTAL;

        int row = 0;
        addField(form, gbc, row++, "DNI", dniAltaField);

        JButton buscarButton = new JButton("Buscar ciudadano");
        buscarButton.addActionListener(event -> buscarCiudadano());
        gbc.gridx = 1;
        gbc.gridy = row++;
        form.add(buscarButton, gbc);

        addField(form, gbc, row++, "Nombre completo", nombreField);
        addField(form, gbc, row++, "Email", emailField);
        addField(form, gbc, row++, "Telefono", telefonoField);

        gbc.gridx = 0;
        gbc.gridy = row;
        form.add(new JLabel("Condicion"), gbc);
        gbc.gridx = 1;
        form.add(mayor65Check, gbc);
        row++;

        gbc.gridx = 0;
        gbc.gridy = row;
        form.add(new JLabel("Servicio"), gbc);
        gbc.gridx = 1;
        form.add(servicioCombo, gbc);

        JPanel actions = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JButton guardarButton = new JButton("Sacar turno");
        guardarButton.addActionListener(event -> sacarTurno());
        JButton limpiarButton = new JButton("Limpiar formulario");
        limpiarButton.addActionListener(event -> limpiarAlta());
        actions.add(guardarButton);
        actions.add(limpiarButton);

        panel.add(form, BorderLayout.NORTH);
        panel.add(actions, BorderLayout.CENTER);
        panel.add(new JScrollPane(salidaAltaArea), BorderLayout.SOUTH);
        return panel;
    }

    private JPanel crearPanelConsulta() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        top.add(new JLabel("DNI"));
        top.add(dniConsultaField);

        JButton buscarButton = new JButton("Ver mis turnos");
        buscarButton.addActionListener(event -> cargarTurnos());
        JButton pagarButton = new JButton("Marcar pagado");
        pagarButton.addActionListener(event -> pagarTurnoSeleccionado());
        JButton cancelarButton = new JButton("Cancelar turno");
        cancelarButton.addActionListener(event -> cancelarTurnoSeleccionado());

        top.add(buscarButton);
        top.add(pagarButton);
        top.add(cancelarButton);

        panel.add(top, BorderLayout.NORTH);
        panel.add(new JScrollPane(turnosTable), BorderLayout.CENTER);
        panel.add(new JScrollPane(salidaConsultaArea), BorderLayout.SOUTH);
        return panel;
    }

    private JPanel crearPanelServicios() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        JTextArea text = new JTextArea();
        text.setEditable(false);
        text.setText("""
                Servicios disponibles:

                1. Licencia de conducir
                   - Turno arancelado.
                   - Genera un pago pendiente.
                   - Aplica 30% de descuento si el ciudadano es mayor de 65 anos.

                2. Asistencia social alimentaria
                   - Turno gratuito.
                   - No genera pago.
                """);

        panel.add(new JScrollPane(text), BorderLayout.CENTER);
        return panel;
    }

    private void addField(JPanel panel, GridBagConstraints gbc, int row, String label, JTextField field) {
        gbc.gridx = 0;
        gbc.gridy = row;
        panel.add(new JLabel(label), gbc);
        gbc.gridx = 1;
        panel.add(field, gbc);
    }

    private void buscarCiudadano() {
        String dni = dniAltaField.getText().trim();
        if (dni.isBlank()) {
            mostrarError("Ingrese un DNI para buscar.");
            return;
        }

        ejecutarAsync(() -> {
            Ciudadano ciudadano = gestorTurnos.buscarCiudadanoPorDni(dni);
            SwingUtilities.invokeLater(() -> {
                if (ciudadano == null) {
                    desbloquearDatosCiudadano();
                    salidaAltaArea.setText("Ciudadano no encontrado. Complete los datos para crearlo.\n");
                    return;
                }

                nombreField.setText(ciudadano.nombreCompleto());
                emailField.setText(ciudadano.email() != null ? ciudadano.email() : "");
                telefonoField.setText(ciudadano.telefono() != null ? ciudadano.telefono() : "");
                mayor65Check.setSelected(ciudadano.mayor65());
                bloquearDatosCiudadano();
                salidaAltaArea.setText("Ciudadano encontrado: " + ciudadano.nombreCompleto() + "\n");
            });
        });
    }

    private void sacarTurno() {
        SolicitudTurno solicitud = new SolicitudTurno(
                dniAltaField.getText().trim(),
                nombreField.getText().trim(),
                emailField.getText().trim(),
                telefonoField.getText().trim(),
                mayor65Check.isSelected(),
                (String) servicioCombo.getSelectedItem()
        );

        if (solicitud.dni().isBlank() || solicitud.nombreCompleto().isBlank()) {
            mostrarError("DNI y nombre completo son obligatorios.");
            return;
        }

        ejecutarAsync(() -> {
            ResultadoTurno resultado = gestorTurnos.sacarTurno(solicitud);
            SwingUtilities.invokeLater(() -> salidaAltaArea.setText(formatearResultado(resultado)));
        });
    }

    private void cargarTurnos() {
        String dni = dniConsultaField.getText().trim();
        if (dni.isBlank()) {
            mostrarError("Ingrese un DNI para consultar.");
            return;
        }

        ejecutarAsync(() -> {
            List<TurnoDetalle> turnos = gestorTurnos.obtenerTurnosPorDni(dni);
            SwingUtilities.invokeLater(() -> mostrarTurnos(turnos));
        });
    }

    private void pagarTurnoSeleccionado() {
        Integer idTurno = obtenerIdSeleccionado();
        if (idTurno == null) {
            mostrarError("Seleccione un turno de la tabla.");
            return;
        }

        String dni = dniConsultaField.getText().trim();
        ejecutarAsync(() -> {
            gestorTurnos.pagarTurnoArancelado(dni, idTurno);
            List<TurnoDetalle> turnos = gestorTurnos.obtenerTurnosPorDni(dni);
            SwingUtilities.invokeLater(() -> {
                mostrarTurnos(turnos);
                salidaConsultaArea.setText("Turno " + idTurno + " marcado como pagado.\n");
            });
        });
    }

    private void cancelarTurnoSeleccionado() {
        Integer idTurno = obtenerIdSeleccionado();
        if (idTurno == null) {
            mostrarError("Seleccione un turno de la tabla.");
            return;
        }

        String dni = dniConsultaField.getText().trim();
        ejecutarAsync(() -> {
            gestorTurnos.cancelarTurno(dni, idTurno);
            List<TurnoDetalle> turnos = gestorTurnos.obtenerTurnosPorDni(dni);
            SwingUtilities.invokeLater(() -> {
                mostrarTurnos(turnos);
                salidaConsultaArea.setText("Turno " + idTurno + " marcado como cancelado.\n");
            });
        });
    }

    private Integer obtenerIdSeleccionado() {
        int selectedRow = turnosTable.getSelectedRow();
        if (selectedRow < 0) {
            return null;
        }

        int modelRow = turnosTable.convertRowIndexToModel(selectedRow);
        return (Integer) turnosTableModel.getValueAt(modelRow, 0);
    }

    private void mostrarTurnos(List<TurnoDetalle> turnos) {
        turnosTableModel.setRowCount(0);

        for (TurnoDetalle turno : turnos) {
            turnosTableModel.addRow(new Object[]{
                    turno.idTurno(),
                    turno.nombreServicio(),
                    turno.fechaHora(),
                    turno.estado(),
                    turno.esArancelado() ? "Arancelado" : "Gratuito",
                    turno.mayor65() ? "Si" : "No",
                    turno.montoOriginal() != null ? turno.montoOriginal() : 0.0,
                    turno.descuentoAplicado() != null ? turno.descuentoAplicado() : 0.0,
                    turno.montoFinal() != null ? turno.montoFinal() : 0.0,
                    turno.estadoPago() != null ? turno.estadoPago() : "-"
            });
        }

        salidaConsultaArea.setText("Turnos encontrados: " + turnos.size() + "\n");
    }

    private String formatearResultado(ResultadoTurno resultado) {
        StringBuilder builder = new StringBuilder();
        builder.append("Turno guardado correctamente.\n");
        builder.append("ID: ").append(resultado.idTurno()).append('\n');
        builder.append("Detalle: ").append(resultado.detalle()).append('\n');
        builder.append("Fecha y hora: ").append(resultado.fechaHora()).append('\n');

        if (resultado.arancelado()) {
            builder.append("Monto original: $").append(resultado.montoOriginal()).append('\n');
            builder.append("Descuento aplicado: $").append(resultado.descuentoAplicado()).append('\n');
            builder.append("Monto final: $").append(resultado.montoFinal()).append('\n');
        } else {
            builder.append("Turno gratuito.\n");
        }

        return builder.toString();
    }

    private void limpiarAlta() {
        dniAltaField.setText("");
        nombreField.setText("");
        emailField.setText("");
        telefonoField.setText("");
        mayor65Check.setSelected(false);
        desbloquearDatosCiudadano();
        salidaAltaArea.setText("");
    }

    private void bloquearDatosCiudadano() {
        nombreField.setEditable(false);
        emailField.setEditable(false);
        telefonoField.setEditable(false);
        mayor65Check.setEnabled(false);
    }

    private void desbloquearDatosCiudadano() {
        nombreField.setEditable(true);
        emailField.setEditable(true);
        telefonoField.setEditable(true);
        mayor65Check.setEnabled(true);
    }

    private void ejecutarAsync(Operacion operacion) {
        new Thread(() -> {
            try {
                operacion.ejecutar();
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> mostrarError(e.getMessage()));
            }
        }).start();
    }

    private void mostrarError(String mensaje) {
        JOptionPane.showMessageDialog(this, mensaje, "Sistema Municipal de Turnos", JOptionPane.ERROR_MESSAGE);
    }

    @FunctionalInterface
    private interface Operacion {
        void ejecutar() throws Exception;
    }
}
