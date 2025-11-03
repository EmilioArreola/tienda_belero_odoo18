odoo.define('sucursales_carrito.checkout', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    /**
     * Este widget maneja la lógica para mostrar u ocultar el
     * selector de sucursales en la página de checkout.
     */
    publicWidget.registry.SucursalesCheckout = publicWidget.Widget.extend({
        selector: '#shop_checkout', // Se "adhiere" al contenedor principal del checkout
        events: {
            // Escucha cambios en CUALQUIER radio button de método de entrega
            'change input[name="delivery_type"]': '_onDeliveryChange',
        },

        /**
         * @override
         */
        start: function () {
            // Llama a la función _onDeliveryChange() tan pronto como carga la página
            // para verificar el estado inicial (por si "Recoger en tienda" ya está seleccionado).
            this._onDeliveryChange();
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Se dispara cada vez que el usuario cambia el método de entrega.
         * @private
         */
        _onDeliveryChange: function () {
            // Encuentra el radio button que está SELECCIONADO
            var $selectedRadio = this.$('input[name="delivery_type"]:checked');

            if (!$selectedRadio.length) {
                // Si no hay nada seleccionado, no hagas nada
                return;
            }

            // Encuentra la etiqueta (label) de ese radio button y lee su texto
            var labelText = $selectedRadio.closest('label').text().trim();

            // Busca los contenedores de tu combo box (los IDs que definimos en el XML)
            var $sucursalWrapper = this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2');

            // LA LÓGICA PRINCIPAL:
            // Si el texto de la etiqueta seleccionada INCLUYE "Recoger en tienda"
            if (labelText.includes('Recoger en tienda')) {
                // ... muéstralo
                $sucursalWrapper.removeClass('d-none');
            } else {
                // ... si no (ej. eligió "Envío a domicilio"), ocúltalo
                $sucursalWrapper.addClass('d-none');
            }
        },
    });

    return publicWidget.registry.SucursalesCheckout;
});