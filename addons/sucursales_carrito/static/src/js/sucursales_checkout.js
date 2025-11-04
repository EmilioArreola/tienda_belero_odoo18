odoo.define('sucursales_carrito.checkout', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SucursalesCheckout = publicWidget.Widget.extend({
        selector: '#shop_checkout',
        events: {
            'change input[name="delivery_type"]': '_onDeliveryChange',
        },

        start: function () {
            this._onDeliveryChange();
            return this._super.apply(this, arguments);
        },

        _onDeliveryChange: function () {
            var $selectedRadio = this.$('input[name="delivery_type"]:checked');

            if (!$selectedRadio.length) {
                return;
            }

            var labelText = $selectedRadio.closest('label').text().trim();

            // ---------- [ INICIO DE DEBUG ] ----------
            // Agrega esta línea para ver qué texto está leyendo:
            console.log("Texto de la etiqueta seleccionada:", labelText);
            // ---------- [ FIN DE DEBUG ] ----------

            var $sucursalWrapper = this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2');

            // Vamos a hacer la comparación más robusta (minúsculas)
            if (labelText.toLowerCase().includes('recoger en tienda')) {

                // Agrega esta línea para saber si entró al IF
                console.log("¡Coincidencia! Mostrando sucursales.");

                $sucursalWrapper.removeClass('d-none');
            } else {
                $sucursalWrapper.addClass('d-none');
            }
        },
    });

    return publicWidget.registry.SucursalesCheckout;
});