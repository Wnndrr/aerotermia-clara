/* Calculadora de Guía de Aerotermia. Método explicado en /calculadora/ */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  if (!$('calc')) return;

  // Rendimiento del sistema actual, precio por defecto del combustible (€/kWh) y cuota fija anual
  var SISTEMAS = {
    gas:     { rend: 0.92, precio: 0.08, fijo: 100 },
    gasoleo: { rend: 0.85, precio: 0.15, fijo: 0 },
    propano: { rend: 0.90, precio: 0.14, fijo: 0 },
    elec:    { rend: 1.00, precio: null, fijo: 0 }
  };
  // Rendimiento estacional (SCOP) de la aerotermia según los emisores
  var SCOP = { exist: 3.0, baja: 3.8, suelo: 4.3, 'suelo-hecho': 4.3 };
  var SCOP_ACS = 2.8;      // agua caliente
  var ACS_KWH = 2000;      // demanda anual de agua caliente de un hogar medio
  // Precio de instalación con radiadores: [m², mínimo, máximo]
  var PRECIOS = [[70, 6500, 9500], [100, 7000, 12000], [150, 12000, 18000], [200, 17000, 22000]];

  function interpolar(m2, col) {
    var p = PRECIOS;
    if (m2 <= p[0][0]) return p[0][col] * Math.max(0.85, m2 / p[0][0]);
    for (var i = 1; i < p.length; i++) {
      if (m2 <= p[i][0]) {
        var t = (m2 - p[i - 1][0]) / (p[i][0] - p[i - 1][0]);
        return p[i - 1][col] + t * (p[i][col] - p[i - 1][col]);
      }
    }
    var u = p[p.length - 1];
    return u[col] * (m2 / u[0]);
  }
  function euros(n) { return Math.round(n / 10) * 10; }
  function miles(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function fmt(n) { return miles(n) + ' €'; }

  function calcular() {
    var m2 = Math.min(400, Math.max(30, parseFloat($('c-m2').value) || 100));
    var zona = parseFloat($('c-zona').value);
    var sis = SISTEMAS[$('c-sis').value];
    var em = $('c-em').value;
    var luz = parseFloat($('c-luz').value) || 0.18;
    var comb = $('c-sis').value === 'elec' ? luz : (parseFloat($('c-comb').value) || sis.precio);

    var calef = m2 * zona;
    var ahora = (calef + ACS_KWH) / sis.rend * comb + sis.fijo;
    var aero = (calef / SCOP[em] + ACS_KWH / SCOP_ACS) * luz;
    var ahorro = ahora - aero;

    var min = interpolar(m2, 1), max = interpolar(m2, 2);
    if (em === 'suelo') { min += m2 * 40; max += m2 * 70; }
    min = Math.round(min / 100) * 100; max = Math.round(max / 100) * 100;

    $('r-precio').textContent = miles(min) + '–' + fmt(max);
    $('r-ahora').textContent = fmt(euros(ahora));
    $('r-aero').textContent = fmt(euros(aero));
    if (ahorro > 20) {
      $('r-ahorro').textContent = fmt(euros(ahorro));
      var a1 = Math.round(min / ahorro), a2 = Math.round(max / ahorro);
      $('r-anos').textContent = a1 > 30 ? 'Más de 30' : (a2 > 30 ? a1 + ' a más de 30' : a1 + '–' + a2);
    } else {
      $('r-ahorro').textContent = 'Sin ahorro';
      $('r-anos').textContent = 'No se recupera';
    }
  }

  $('c-sis').addEventListener('change', function () {
    var s = SISTEMAS[this.value];
    $('c-comb').value = s.precio === null ? $('c-luz').value : s.precio;
    $('c-comb').disabled = s.precio === null;
  });
  $('calc').addEventListener('input', calcular);
  $('calc').addEventListener('change', calcular);
  calcular();
})();
