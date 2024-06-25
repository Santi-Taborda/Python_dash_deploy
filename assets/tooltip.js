window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.Hora_legible = function(value) {
     // Multiplicamos por 1000 para convertir el timestamp en milisegundos
     var date = new Date(value*1000);

     // Formateamos la fecha y hora
     var formattedDate = date.toLocaleString('es-CO', {
          timeZone:'UTC',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
       });

     return (formattedDate);
}
