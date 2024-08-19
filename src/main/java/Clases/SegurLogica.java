/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package Clases;

import Formularios.LogIn;
import java.util.Arrays;
import javax.swing.JOptionPane;
import javax.swing.JPasswordField;
import javax.swing.JTextField;

public class SegurLogica {
    
    public void CambiaContra (JTextField user, JPasswordField con, JPasswordField confCont){
       
       if (Arrays.equals(con.getPassword(),confCont.getPassword())){
           LogIn.USsuario = user.getText();
           String conString = new String(con.getPassword());
           LogIn.Contra = conString;
       } 
       else{
            JOptionPane.showMessageDialog(null, "Las contraseñas digitadas no son las mismas");
       }   
    }
}
