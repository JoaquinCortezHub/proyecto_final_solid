package com.municipio.turnos;

import com.municipio.turnos.servicios.GestorTurnos;
import com.municipio.turnos.servicios.SupabaseClient;
import com.municipio.turnos.ui.SistemaTurnosFrame;

import javax.swing.JOptionPane;
import javax.swing.SwingUtilities;

public class Main {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> { //Con esto nos aseguramos de que los cambios en Swing se hagan en el hilo correcto
            try {
                SupabaseClient supabaseClient = new SupabaseClient(); // DB
                GestorTurnos gestorTurnos = new GestorTurnos(supabaseClient); //Lógica para agendar turnos
                new SistemaTurnosFrame(gestorTurnos).setVisible(true); // Interfaz gráfica
            } catch (Exception e) {
                JOptionPane.showMessageDialog(
                        null,
                        e.getMessage(),
                        "No se pudo iniciar el sistema",
                        JOptionPane.ERROR_MESSAGE
                );
            }
        });
    }
}
