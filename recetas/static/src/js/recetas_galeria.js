odoo.define('recetas.recetas_galeria', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');

    publicWidget.registry.RecetasGaleria = publicWidget.Widget.extend({
        selector: '.ver-receta',
        events: {
            'click': '_onClickVerReceta',
        },

        _onClickVerReceta: function (ev) {
            ev.preventDefault();
            const recetaId = ev.currentTarget.dataset.id;

            ajax.jsonRpc(`/recetas/detalle/${recetaId}`, 'call', {}).then(function (data) {
                $('#modalRecetaTitulo').text(data.nombre);
                $('#modalRecetaContenido').html(`
                    <img src="${data.imagen}" class="img-fluid mb-3 rounded" />
                    <p><strong>Dificultad:</strong> ${data.dificultad}</p>
                    <p><strong>Porciones:</strong> ${data.porciones}</p>
                    <p><strong>Tiempo total:</strong> ${data.tiempo_total} minutos</p>
                    <hr/>
                    <h4>Ingredientes</h4>
                    <p>${data.ingredientes.replace(/\n/g, "<br/>")}</p>
                    <h4>Preparación</h4>
                    <div>${data.preparacion}</div>
                `);
                $('#modalReceta').modal('show');
            });
        }
    });

    return publicWidget.registry.RecetasGaleria;
});
