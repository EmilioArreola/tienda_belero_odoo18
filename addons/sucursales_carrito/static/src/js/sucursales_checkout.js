/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// --- MENSAJE 1 ---
console.log("✅ Archivo sucursales_checkout.js ¡CARGADO! (Odoo 18)");

/**
 * Widget para mostrar/ocultar selector de sucursales
 * en el checkout cuando se selecciona "Recoger en tienda"
 */
publicWidget.registry.SucursalesCheckout = publicWidget.Widget.extend({
    selector: '#wrap',  // Selector más amplio para asegurar que se cargue
    events: {
        'change input[name="delivery_type"]': '_onDeliveryChange',
    },

    /**
     * @override
     */
    start: function () {
        console.log("🚀 Widget SucursalesCheckout INICIADO");
        this._onDeliveryChange();
        return this._super.apply(this, arguments);
    },

    /**
     * Maneja el cambio de método de entrega
     * @private
     */
    _onDeliveryChange: function () {
        console.log("🖱️ Evento _onDeliveryChange() disparado");

        const $selectedRadio = this.$('input[name="delivery_type"]:checked');

        if (!$selectedRadio.length) {
            console.warn("⚠️ No se encontró ningún radio button seleccionado");
            return;
        }

        const selectedValue = $selectedRadio.val();
        console.log("🔵 Valor seleccionado:", selectedValue);

        const $sucursalWrapper = this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2');

        if (!$sucursalWrapper.length) {
            console.error("❌ ERROR: No se encontró #sucursal_picker_wrapper");
            return;
        }

        // Mostrar si el valor es '0' (Recoger en tienda)
        if (selectedValue === '0') {
            console.log("✅ Mostrando selector de sucursales");
            $sucursalWrapper.removeClass('d-none');
        } else {
            console.log("👎 Ocultando selector de sucursales");
            $sucursalWrapper.addClass('d-none');
        }
    },
});

export default publicWidget.registry.SucursalesCheckout;