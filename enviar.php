<?php 
    $nombre = $_POST['name']; 
    $email = $_POST['email']; 
    $mensaje = $_POST['missatge'];
    $asunto = 'Missatge del client'; 
   
    $contenido = "Nom client: $nombre\n";
    $contenido .= "Email: $email\n";
    $contenido .= "Missatge: $mensaje\n";

    mail('blanca.navas.cerezuela@estudiantat.upc.edu', $asunto, $contenido);
    echo "Correu enviat"; 
?>
