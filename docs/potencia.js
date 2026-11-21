/* Calculadora de potencia de Guía de Aerotermia. Método explicado en /calculadora-potencia/ */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  if (!$('pot')) return;

  // Vatios por m² con techos de 2,5 m. Filas: aislamiento bueno, medio, malo.
  // Columnas: clima suave, templado, frío, muy frío.
  var W_M2 = [
    [45, 50, 60, 70],
    [60, 65, 80, 90],
    [75, 90, 110, 125]
  ];
  // Potencias nominales habituales en el catálogo de los fabricantes (kW)
  var MODELOS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 25, 30];
  var COP_DISENO = 2.5; // rendimiento aproximado en el día más frío

  function coma(n, dec) { return n.toFixed(dec).replace('.', ','); }

  function calcular() {
    var m2 = Math.min(500, Math.max(20, parseFloat($('p-m2').value) || 100));
    var alt = parseFloat($('p-alt').value);
    var zona = parseInt($('p-zona').value, 10);
    var ais = parseInt($('p-ais').value, 10);
    var tipo = parseFloat($('p-tipo').value);

    var kw = m2 * W_M2[ais][zona] * (alt / 2.5) * tipo / 1000;
    var modelo = MODELOS[MODELOS.length - 1];
    for (var i = 0; i < MODELOS.length; i++) {
      if (MODELOS[i] >= kw) { modelo = MODELOS[i]; break; }
    }
    $('p-calc').textContent = coma(kw, 1) + ' kW';
    $('p-equipo').textContent = kw > 30 ? 'Más de 30 kW' : modelo + ' kW';
    $('p-alerta').textContent = coma(Math.max(modelo, kw * 1.3), 0) + ' kW';
    $('p-elec').textContent = coma(modelo / COP_DISENO, 1) + ' kW';
  }

  $('pot').addEventListener('input', calcular);
  $('pot').addEventListener('change', calcular);
  calcular();
})();
