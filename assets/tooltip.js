window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.Hora_legible = function(value) {
     // Multiplicamos por 1000 para convertir el timestamp en milisegundos
     var date = new Date(value*1000);
     var real_year= date.getUTCFullYear()
     var real_month= date.getUTCMonth()
     var days= date.getUTCDate()
     var hours= date.getUTCHours()+6
     var minutes= date.getUTCMinutes()-10
     var days_real=days
     var hours_real=hours
     var minutes_real=minutes


     if (minutes<0)
          minutes_real=minutes+60
          hours_real= hours_real-1
          if (hours_real==-1)
               hours_real=23
               days_real=days_real-1
               
     var hora_transformed= ""+days_real+"/"+real_month+"/"+real_year+"   "+hours_real+":"+minutes_real
     
/*      // Formateamos la fecha y hora
     var formattedDate = date.toLocaleString('es-CO', {
          timeZone: 'UTC',
           year: 'numeric',
           month: '2-digit',
           day: '2-digit',
           hour: '2-digit',
           minute: '2-digit',
           second: '2-digit'
       }); */

     return (formattedDate);
}
