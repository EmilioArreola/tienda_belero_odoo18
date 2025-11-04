odoo.define('sucursales_carrito.checkout', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    // --- MENSAJE 1 ---
    // Este mensaje debe aparecer tan pronto como la página cargue, 
    // si no aparece, el archivo JS no se está cargando.
    console.log("✅ Archivo sucursales_checkout.js ¡CARGADO!");

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
            // --- MENSAJE 2 ---
            // Si ves el Mensaje 1 pero no este, el 'selector' está mal.
            console.log("🚀 Widget SucursalesCheckout INICIADO y adjunto a #shop_checkout.");

            // Llama a la función _onDeliveryChange() tan pronto como carga la página
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
            // --- MENSAJE 3 ---
            // Deberías ver esto CADA VEZ que haces clic en un método de entrega.
            console.log("🖱️ Evento _onDeliveryChange() disparado.");

            // Encuentra el radio button que está SELECCIONADO
            var $selectedRadio = this.$('input[name="delivery_type"]:checked');

            if (!$selectedRadio.length) {
                console.warn("No se encontró ningún radio button seleccionado.");
                return; // No hay nada seleccionado
            }

            // --- [ INICIO DE LA LÓGICA MEJORADA ] ---
            var selectedValue = $selectedRadio.val();

            // --- MENSAJE 4 ---
            // Este es el mensaje más importante.
            console.log("🔵 Valor del radio button seleccionado:", selectedValue);

            var $sucursalWrapper = this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2');

            if (!$sucursalWrapper.length) {
                console.error("¡ERROR! No se encontró el div #sucursal_picker_wrapper. Revisa el XML.");
                return;
            }

            // Comparamos por VALOR ('0') en lugar de TEXTO
            if (selectedValue === '0') {
                // --- MENSAJE 5 (ÉXITO) ---
                console.log("👍 ¡Coincidencia! Mostrando sucursales (valor '0').");
                $sucursalWrapper.removeClass('d-none');
            } else {
                // --- MENSAJE 6 (FALLO) ---
                console.log("❌ No es '0'. Ocultando sucursales.");
                $sucursalWrapper.addClass('d-none');
            }
        },
    });

    return publicWidget.registry.SucursalesCheckout;
});