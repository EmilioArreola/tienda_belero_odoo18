odoo.define('recetas.gallery_alternative', function (require) {
    'use strict';

    const rpc = require('web.rpc');
    
    // Usamos una construcción estándar de jQuery para asegurar que el DOM esté listo.
    $(document).ready(function () {

        // En lugar de un widget, creamos un detector de eventos (listener) directamente.
        // Escuchamos por clics en cualquier elemento con la clase '.ver-receta'
        // que esté dentro de un elemento con el id '#recetas_gallery'.
        $('#recetas_gallery').on('click', '.ver-receta', function (ev) {
            ev.preventDefault();
            
            const $card = $(ev.currentTarget);
            const recetaId = parseInt($card.data('id'));
            const $modal = $('#modalReceta');

            if (!recetaId || !$modal.length) {
                console.error("No se encontró el ID de la receta o el modal.");
                return;
            }

            // --- La lógica de adentro es la misma que ya teníamos ---
            $modal.modal('show');
            $modal.find('.modal-body').html('<div class="text-center py-5"><i class="fa fa-spinner fa-spin fa-3x"></i></div>');
            $modal.find('.modal-title').text('Cargando...');
            
            rpc.query({
                model: 'recetas.receta',
                method: 'search_read',
                args: [[['id', '=', recetaId]], [
                    'name', 'imagen', 'dificultad', 'porciones', 
                    'tiempo_total', 'ingredientes', 'preparacion'
                ]],
            }).then((data) => {
                if (data.length > 0) {
                    const receta = data[0];
                    const dificultad = {facil: 'Fácil', medio: 'Medio', dificil: 'Difícil'};
                    const contenidoHtml = `
                        <img src="/web/image/recetas.receta/${receta.id}/imagen" class="img-fluid mb-3 rounded" alt="${receta.name}" />
                        <p><strong>Dificultad:</strong> ${dificultad[receta.dificultad] || 'No especificada'}</p>
                        <p><strong>Porciones:</strong> ${receta.porciones || 0}</p>
                        <p><strong>Tiempo total:</strong> ${receta.tiempo_total || 0} minutos</p>
                        <hr/>
                        <h4>Ingredientes</h4>
                        <div>${receta.ingredientes ? receta.ingredientes.replace(/\n/g, "<br/>") : 'No especificados'}</div>
                        <hr/>
                        <h4>Preparación</h4>
                        <div>${receta.preparacion || 'No especificada'}</div>
                    `;
                    $modal.find('.modal-title').text(receta.name);
                    $modal.find('.modal-body').html(contenidoHtml);
                } else {
                     $modal.find('.modal-body').html('<p class="text-danger">No se pudo encontrar la receta.</p>');
                }
            });
        });
    });
});