/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ Archivo sucursales_checkout.js ¡CARGADO! (Odoo 18)");

/**
 * Widget para mostrar/ocultar selector de sucursales
 * en el checkout cuando se selecciona "Recoger en tienda"
 */
publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        // Evento específico para los radio buttons de Odoo
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'click label.o_delivery_carrier_label': '_alCambiarMetodoEntrega',
    },

    /**
     * @override
     */
    start: function () {
        console.log("🚀 Widget SelectorSucursales INICIADO");

        // Esperamos un poco para que el DOM esté completamente cargado
        setTimeout(() => {
            this._alCambiarMetodoEntrega();
        }, 300);

        return this._super.apply(this, arguments);
    },

    /**
     * Maneja el cambio de método de entrega
     * @private
     */
    _alCambiarMetodoEntrega: function () {
        console.log("🖱️ Evento _alCambiarMetodoEntrega() disparado");

        // Buscamos el radio button seleccionado
        const $radioSeleccionado = this.$('input[name="o_delivery_radio"]:checked');

        console.log("🔍 Total de radios encontrados:", this.$('input[name="o_delivery_radio"]').length);
        console.log("🔍 Radio seleccionado:", $radioSeleccionado.length);

        if (!$radioSeleccionado.length) {
            console.warn("⚠️ No se encontró ningún radio button seleccionado");
            this._ocultarSucursales();
            return;
        }

        // Obtenemos el ID del delivery method
        const idMetodoEntrega = $radioSeleccionado.attr('data-dm-id');
        const tipoEntrega = $radioSeleccionado.attr('data-delivery-type');

        // Buscamos el label asociado
        const idRadio = $radioSeleccionado.attr('id');
        const $label = this.$('label[for="' + idRadio + '"]');
        const textoLabel = $label.text().trim().toLowerCase();

        console.log("🔵 ID del método:", idMetodoEntrega);
        console.log("🔵 Tipo de entrega:", tipoEntrega);
        console.log("📝 Texto del label:", textoLabel);

        // Verificamos si es "Recoger en tienda"
        const esRecogerEnTienda = textoLabel.includes('recoger') ||
            textoLabel.includes('tienda') ||
            tipoEntrega === 'fixed' && textoLabel.includes('gratis');

        if (esRecogerEnTienda) {
            console.log("✅ ¡ES RECOGER EN TIENDA! Mostrando selector de sucursales");
            this._mostrarSucursales();
        } else {
            console.log("👎 NO es recoger en tienda. Ocultando selector de sucursales");
            this._ocultarSucursales();
        }
    },

    /**
     * Muestra el selector de sucursales
     * @private
     */
    _mostrarSucursales: function () {
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');

        if (!$contenedorSucursales.length) {
            console.error("❌ ERROR: No se encontró #sucursal_picker_wrapper");
            return;
        }

        $contenedorSucursales.removeClass('d-none').show();

        // Hacer scroll suave hacia las sucursales
        setTimeout(() => {
            $contenedorSucursales[0].scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }, 100);
    },

    /**
     * Oculta el selector de sucursales
     * @private
     */
    _ocultarSucursales: function () {
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');
        $contenedorSucursales.addClass('d-none').hide();

        // Limpiar la selección
        this.$('#sucursal_select').val('');
    },
});

export default publicWidget.registry.SelectorSucursales;