/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package Clases;

import Clases.CConexion;
import com.toedter.calendar.JDateChooser;
import java.awt.HeadlessException;
import java.awt.Image;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import javax.imageio.stream.FileImageInputStream;
import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author juanl
 */
public class CUsuarios {
    
    int id;

    public void establecerId(int id) {
        this.id = id; // Corregir el nombre de la variable
    }
       
    public void MostrarComboBox(JComboBox comboBoxIngreso) { // Corregir el nombre del método
        Clases.CConexion objetoConexion = new Clases.CConexion();
 
        String sql = "select * from Ingreso;"; // Corregir la consulta SQL
        
        try (Statement st = objetoConexion.estableceConexion().createStatement()) {
            ResultSet rs = st.executeQuery(sql);
            comboBoxIngreso.removeAllItems();
     
            while (rs.next()) {
                String nombreSexo = rs.getString("Ingreso");
                int id = rs.getInt("id"); // Usar una variable local para 
                comboBoxIngreso.addItem(nombreSexo);
                comboBoxIngreso.putClientProperty(nombreSexo, id);
            }
             
        } catch (SQLException e) {
            JOptionPane.showMessageDialog(null, "Error al mostrar ingreso: " + e.toString());
        } finally {
            objetoConexion.cerrarConexion();
        }
    }

    public void  AgregarUsuario(JTextField nombres,JTextField apellidos,JComboBox comboBoxIngreso,JTextField edad, JDateChooser fnacimiento, File foto, JTextField Documento ){
    
        CConexion objetoConexion = new CConexion();
 
        String consulta="INSERT INTO usuarios (nombres, apellidos, fkIngreso, edad, Fingreso, foto, Documento) VALUES (?,?,?,?,?,?,?);";

        FileInputStream fis = null;
        try {
            
            if (foto != null && foto.exists()) {
                fis = new FileInputStream(foto);
            }
            
            CallableStatement cs = objetoConexion.estableceConexion().prepareCall(consulta);
            
            String nombre = nombres.getText().trim();
            cs.setString(1, nombre.isEmpty() ? null : nombre);

            String apellido = apellidos.getText().trim();
            cs.setString(2, apellido.isEmpty() ? null : apellido);
            
            Object selectedItem = comboBoxIngreso.getSelectedItem();
            int id = (selectedItem != null && comboBoxIngreso.getClientProperty(selectedItem) instanceof Integer)
                ? (int) comboBoxIngreso.getClientProperty(selectedItem)
                : null;
            cs.setObject(3, id);
            
            String edadText = edad.getText().trim();
            cs.setObject(4, edadText.isEmpty() ? null : Integer.parseInt(edadText));
            
            Date fechaSeleccionada = fnacimiento.getDate();
            cs.setDate(5, fechaSeleccionada != null ? new java.sql.Date(fechaSeleccionada.getTime()) : null);
            
            if (fis != null) {
            cs.setBinaryStream(6, fis, (int) foto.length());
            } else {
            cs.setBinaryStream(6, null);
            }
            
            String documento = Documento.getText().trim();
            cs.setString(7, documento.isEmpty() ? null : documento);
     
             cs.execute();
     
            JOptionPane.showMessageDialog(null,"Se guardo el usuario correctamente");
        } 
        catch (HeadlessException | FileNotFoundException | NumberFormatException | SQLException e) {
            JOptionPane.showMessageDialog(null,"Error al guardar, error: "+e.toString());
        }
        finally {
        // Asegurarse de cerrar el FileInputStream
        if (fis != null) {
            try {
                fis.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}

public void MostrarUsuarios(JTable tablaTotalUsuarios){            
    
    Clases.CConexion objetoConexion = new Clases.CConexion();
 
    DefaultTableModel modelo = new DefaultTableModel();
 
    String sql="";
 
    modelo.addColumn("ID");
    modelo.addColumn("Nombres");
    modelo.addColumn("Apellidos");
    modelo.addColumn("Igreso");
    modelo.addColumn("Edad");
    modelo.addColumn("F.ingreso"); 
    modelo.addColumn("Foto");
    modelo.addColumn("Documento");
 
    tablaTotalUsuarios.setModel(modelo);
    
        sql = "SELECT usuarios.id, usuarios.nombres, usuarios.apellidos, Ingreso.Ingreso, usuarios.edad, usuarios.Fingreso, usuarios.foto, usuarios.Documento FROM usuarios INNER JOIN Ingreso ON usuarios.fkIngreso = Ingreso.id;";
 
    try {
        Statement st = objetoConexion.estableceConexion().createStatement();
        ResultSet rs = st.executeQuery(sql);
     
        while(rs.next()){
         
            String id = rs.getString("id");
            String nombres = rs.getString("nombres");
            String apellidos = rs.getString("apellidos");
            String sexo = rs.getString("Ingreso");
            String edad = rs.getString("edad");
     
            SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy;");
            java.sql.Date fechaSQL = rs.getDate("Fingreso");
            String nuevaFecha = sdf.format(fechaSQL);
            String Documento = rs.getString("Documento");
     
            byte [] imageBytes = rs.getBytes("foto");
            Image foto = null;
     
            if (imageBytes !=null){
     
                try {
                    ImageIcon imageIcon = new ImageIcon(imageBytes);
                    foto= imageIcon.getImage();
                } catch (Exception e) {
                    JOptionPane.showMessageDialog(null,"Eror:"+ e.toString());
                }
         
                modelo.addRow(new Object[]{id,nombres,apellidos,sexo,edad,nuevaFecha,foto,Documento});
            }
     
            tablaTotalUsuarios.setModel(modelo);
        }    
    } catch (HeadlessException | SQLException e) {
     
        JOptionPane.showMessageDialog(null,"Eror al mostrar usuarios, error:"+ e.toString());
        
    } finally{
 
        objetoConexion.cerrarConexion();
    }
}
 
    public void Seleccionar(JTable tbusuarios, JTextField txtid, JTextField txtnombres, JTextField txtapellidos, JComboBox<String> cbIngreso, JTextField txtedad, JDateChooser dffechanacimiento, JLabel lblimagen, JTextField Txtdocumento) {
       
        int fila = tbusuarios.getSelectedRow();
        
        if(fila>=0){
            
            Object id = tbusuarios.getValueAt(fila, 0);
            Object nombres = tbusuarios.getValueAt(fila, 1);
            Object apellidos = tbusuarios.getValueAt(fila, 2);
            Object ingreso = tbusuarios.getValueAt(fila, 3);
            Object edad = tbusuarios.getValueAt(fila, 4);
            Object fecha = tbusuarios.getValueAt(fila, 5);
            Object imagen = tbusuarios.getValueAt(fila, 6);
            Object documento = tbusuarios.getValueAt(fila, 7);
            
            
             // Establecer los valores en los componentes, manejando valores nulos
        txtid.setText(id != null ? id.toString() : "");
        txtnombres.setText(nombres != null ? nombres.toString() : "");
        txtapellidos.setText(apellidos != null ? apellidos.toString() : "");
        Txtdocumento.setText(documento != null ? documento.toString() : "" );
        
        // Aquí asumimos que el JComboBox se ha llenado con las opciones correspondientes
        if (ingreso != null) {
            cbIngreso.setSelectedItem(ingreso.toString());
        } else {
            cbIngreso.setSelectedItem(null);
        }

        txtedad.setText(edad != null ? edad.toString() : "");

        if (fecha != null) {
            try {
                // Aquí suponemos que el formato de fecha en la tabla es compatible con SimpleDateFormat
                SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy"); // Cambia el formato según tu base de datos
                Date fechaDate = sdf.parse(fecha.toString());
                dffechanacimiento.setDate(fechaDate);
            } catch (ParseException e) {
                JOptionPane.showMessageDialog(null, "Error al seleccionar la fecha, error: " + e.toString());
            }
        } else {
            dffechanacimiento.setDate(null);
        }

        if (imagen != null && imagen instanceof Image) {
            // Escalar imagen
            ImageIcon originalIcon = new ImageIcon((Image) imagen);
            int lblanchura = lblimagen.getWidth();
            int lblaltura = lblimagen.getHeight();
            Image imagenEscalada = originalIcon.getImage().getScaledInstance(lblanchura, lblaltura, Image.SCALE_SMOOTH);
            lblimagen.setIcon(new ImageIcon(imagenEscalada));
        } else {
            lblimagen.setIcon(null); // Limpiar la imagen si es nula
            }
        }
    }  
    
    
public void ModificarUsuarios(JTextField id, JTextField nombres, JTextField apellidos, JComboBox comboBoxIngreso, JTextField edad, JDateChooser fnacimiento, File foto, JTextField Documento) {
    CConexion objetoConexion = new CConexion();
    
    String consulta = "UPDATE Usuarios SET nombres=?, apellidos=?, fkIngreso=?, edad=?, Fingreso=?, foto=?, Documento=? WHERE id=?";
    
    try {
        FileInputStream fis = new FileInputStream(foto);
        PreparedStatement ps = objetoConexion.estableceConexion().prepareStatement(consulta);
        
        
        String nombre = nombres.getText().trim();
        ps.setString(1, nombre.isEmpty() ? null : nombre);
        
        String apellido = apellidos.getText().trim();
        ps.setString(2, apellido.isEmpty() ? null : apellido);
        
        int ingreso = (int) comboBoxIngreso.getClientProperty(comboBoxIngreso.getSelectedItem());
        ps.setInt(3, ingreso);
        
        String edadText = edad.getText().trim();
        ps.setObject(4, edadText.isEmpty() ? null : Integer.parseInt(edadText));
        
        Date fechaSeleccionada = fnacimiento.getDate();
        java.sql.Date fechaSQL = new java.sql.Date(fechaSeleccionada.getTime());
        ps.setDate(5, fechaSQL); 
        
        if (fis != null) {
            ps.setBinaryStream(6, fis, (int) foto.length());
            } else {
            ps.setBinaryStream(6, null);
            }
            
        String documento = Documento.getText().trim();
        ps.setString(7, documento.isEmpty() ? null : documento);
        
        ps.setInt(8, Integer.parseInt(id.getText()));
        
        ps.executeUpdate();
        
        JOptionPane.showMessageDialog(null, "Se modificó correctamente.");
        
    } catch (HeadlessException | FileNotFoundException | NumberFormatException | SQLException e) {
        JOptionPane.showMessageDialog(null, "No se modificó correctamente, error: " + e.toString());
    } finally {
        objetoConexion.cerrarConexion();
    }
}
    public void EliminarUsuario(JTextField id){
     
        CConexion objetoConexion = new CConexion();
     
        String consulta="DELETE FROM usuarios WHERE usuarios.id=?;";
     
        try {
            CallableStatement cs = objetoConexion.estableceConexion().prepareCall(consulta);
             
            cs.setInt(1,Integer.parseInt(id.getText()));
             
            cs.execute();
             
            JOptionPane.showMessageDialog(null,"Se elimino correctamente");
             
        } catch (HeadlessException | NumberFormatException | SQLException e) {
             JOptionPane.showMessageDialog(null, "No se elimino correctamente, error"+e.toString());
        } finally {
             objetoConexion.cerrarConexion();
        }
    }
    
    public void limpriarCampos(JTextField id,JTextField nombres,JTextField apellidos,JTextField edad, JDateChooser Fingreso, JTextField rutaimagen,JLabel imagencontenido, JTextField Documento){
     id.setText("");
     nombres.setText("");
     apellidos.setText("");
     Documento.setText("");
     edad.setText("");
     rutaimagen.setText("");
     Calendar calendario = Calendar.getInstance();
     Fingreso.setDate(calendario.getTime());
     imagencontenido.setIcon(null);
    }
}

