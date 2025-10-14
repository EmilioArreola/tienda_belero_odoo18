odoo.define('modulo_recetas.recetas_search', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');
var core = require('web.core');

var _t = core._t;

publicWidget.registry.RecetasSearch = publicWidget.Widget.extend({
    selector: '.o_recetas_main_container', // El contenedor principal de nuestra página
    events: {
        'input input.o_recetas_search_input': '_onSearchInput',
    },

    /**
     * @override
     */
    start: function () {
        this.$search_input = this.$('input.o_recetas_search_input');
        this.$recetas_container = this.$('.o_recetas_row');
        // 'debounce' es una técnica para no sobrecargar el servidor.
        // Solo ejecuta la búsqueda 500ms después de que el usuario deja de escribir.
        this._onSearch = _.debounce(this._doSearch.bind(this), 500);
        return this._super.apply(this, arguments);
    },

    // 1. Cada vez que el usuario escribe, llamamos a la función debounced.
    _onSearchInput: function () {
        this._onSearch();
    },

    // 2. Esta función realiza la llamada al servidor.
    _doSearch: function () {
        var searchTerm = this.$search_input.val();
        var self = this;
        
        // Usamos RPC para llamar a nuestro método del controlador Python.
        this._rpc({
            route: '/recetas/search_ajax',
            params: {
                search_term: searchTerm,
            },
        }).then(function (data) {
            // 3. Cuando el servidor responde, redibujamos las recetas.
            self.renderRecetas(data);
        });
    },

    // 4. Esta función genera el HTML para las nuevas recetas y lo reemplaza.
    renderRecetas: function (recetas) {
        var newHtml = '';
        if (recetas.length > 0) {
            recetas.forEach(function (receta) {
                // Generamos el HTML de cada tarjeta de receta
                newHtml += `
                    <div class="col-md-4 mb-4">
                        <div class="card h-100">
                            <img src="/web/image/receta.receta/${receta.id}/image_1920" class="card-img-top img-fluid" alt="Imagen de Receta"/>
                            <div class="card-body">
                                <h4 class="card-title">
                                    <a href="/recetas/${receta.id}">${receta.name}</a>
                                </h4>
                                <h6 class="card-subtitle mb-2 text-muted">
                                    <i class="fa fa-tag"/> ${receta.categoria_id ? receta.categoria_id[1] : ''}
                                </h6>
                                <p class="card-text">${receta.descripcion_corta}</p>
                            </div>
                            <div class="card-footer">
                                <a href="/recetas/${receta.id}" class="btn btn-primary">Ver Receta Completa</a>
                            </div>
                        </div>
                    </div>`;
            });
        } else {
            newHtml = `<div class="col-12"><p class="text-center text-muted mt-5">${_t('No se encontraron recetas.')}</p></div>`;
        }
        this.$recetas_container.html(newHtml);
    },
});

return publicWidget.registry.RecetasSearch;

});