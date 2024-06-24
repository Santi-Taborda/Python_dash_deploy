window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.Hora_legible = function(value) {
     // Multiplicamos por 1000 para convertir el timestamp en milisegundos
     var date = new Date(value*1000);
     var real_year= date.getUTCFullYear()
     var real_month= date.getUTCMonth()
     var days= date.getUTCDate()
     var hours= date.getUTCHours()+4
     var minutes= date.getUTCMinutes()+17
     var days_real=days
     var hours_real=hours
     var minutes_real=minutes


     if (minutes>=60)
          minutes_real=minutes-60
          hours_real= hours+1
     
     if (hours>=24)
          days_real=days+1

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

     return (hora_transformed);
}
