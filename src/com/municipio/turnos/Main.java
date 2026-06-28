package com.municipio.turnos;

import com.municipio.turnos.servicios.GestorTurnos;
import com.municipio.turnos.servicios.SupabaseClient;
import com.municipio.turnos.ui.SistemaTurnosFrame;

import javax.swing.JOptionPane;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;

public class Main {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
                SupabaseClient supabaseClient = new SupabaseClient();
                GestorTurnos gestorTurnos = new GestorTurnos(supabaseClient);
                new SistemaTurnosFrame(gestorTurnos).setVisible(true);
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
