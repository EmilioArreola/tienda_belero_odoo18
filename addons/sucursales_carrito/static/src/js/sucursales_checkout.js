/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// --- MENSAJE 1 ---
console.log("✅ Archivo sucursales_checkout.js ¡CARGADO! (Odoo 18)");

/**
 * Widget para mostrar/ocultar selector de sucursales
 * en el checkout cuando se selecciona "Recoger en tienda"
 */
publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        // Odoo usa diferentes selectores para delivery
        'change input[type="radio"][name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'click label.o_delivery_carrier_label': '_alCambiarMetodoEntrega',
        'change input[name="delivery_type"]': '_alCambiarMetodoEntrega',
    },

    /**
     * @override
     */
    start: function () {
        console.log("🚀 Widget SelectorSucursales INICIADO");

        // Esperamos un poco para que el DOM esté listo
        setTimeout(() => {
            this._alCambiarMetodoEntrega();
        }, 500);

        return this._super.apply(this, arguments);
    },

    /**
     * Maneja el cambio de método de entrega
     * @private
     */
    _alCambiarMetodoEntrega: function () {
        console.log("🖱️ Evento _alCambiarMetodoEntrega() disparado");

        // Intentamos encontrar el radio button seleccionado con diferentes selectores
        let $radioSeleccionado = this.$('input[name="o_delivery_radio"]:checked');

        if (!$radioSeleccionado.length) {
            $radioSeleccionado = this.$('input[name="delivery_type"]:checked');
        }

        if (!$radioSeleccionado.length) {
            $radioSeleccionado = this.$('input[type="radio"]:checked').filter(function () {
                return $(this).closest('.o_delivery_carrier_select').length > 0;
            });
        }

        console.log("🔍 Radio buttons encontrados:", this.$('input[type="radio"]').length);
        console.log("🔍 Radio seleccionado:", $radioSeleccionado.length);

        if (!$radioSeleccionado.length) {
            console.warn("⚠️ No se encontró ningún radio button seleccionado");
            // Intentamos buscar por el label que dice "Recoger en tienda"
            this._buscarPorTextoLabel();
            return;
        }

        // Obtenemos el valor y el label asociado
        const valorSeleccionado = $radioSeleccionado.val();
        const $label = $radioSeleccionado.closest('label').length ?
            $radioSeleccionado.closest('label') :
            $('label[for="' + $radioSeleccionado.attr('id') + '"]');

        const textoLabel = $label.text().trim().toLowerCase();

        console.log("🔵 Valor seleccionado:", valorSeleccionado);
        console.log("📝 Texto del label:", textoLabel);

        const $contenedorSucursales = this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2');

        if (!$contenedorSucursales.length) {
            console.error("❌ ERROR: No se encontró #sucursal_picker_wrapper");
            return;
        }

        // Verificamos si es "Recoger en tienda" por valor O por texto
        const esRecogerEnTienda = valorSeleccionado === '0' ||
            valorSeleccionado === 'pickup' ||
            textoLabel.includes('recoger') ||
            textoLabel.includes('tienda') ||
            textoLabel.includes('gratis');

        if (esRecogerEnTienda) {
            console.log("✅ ¡ES RECOGER EN TIENDA! Mostrando selector de sucursales");
            $contenedorSucursales.removeClass('d-none').show();
        } else {
            console.log("👎 NO es recoger en tienda. Ocultando selector de sucursales");
            $contenedorSucursales.addClass('d-none').hide();
        }
    },

    /**
     * Método alternativo: buscar por el texto del label
     * @private
     */
    _buscarPorTextoLabel: function () {
        console.log("🔍 Buscando por texto en los labels...");

        const $todosLosLabels = this.$('label');
        let $labelRecoger = null;

        $todosLosLabels.each(function () {
            const texto = $(this).text().trim().toLowerCase();
            if (texto.includes('recoger') || texto.includes('tienda')) {
                $labelRecoger = $(this);
                console.log("✅ Encontrado label:", texto);
                return false; // break del each
            }
        });

        if ($labelRecoger) {
            const $radioAsociado = $labelRecoger.find('input[type="radio"]');
            if ($radioAsociado.length && $radioAsociado.is(':checked')) {
                console.log("✅ ¡Recoger en tienda está seleccionado!");
                this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2').removeClass('d-none').show();
                return;
            }
        }

        // Si no encontramos nada, ocultamos las sucursales
        this.$('#sucursal_picker_wrapper, #sucursal_picker_wrapper_2').addClass('d-none').hide();
    },
});

export default publicWidget.registry.SelectorSucursales;