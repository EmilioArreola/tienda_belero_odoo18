/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

console.log("✅ SelectorSucursales v15.0 - Secuestro de Formulario");

publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',

    events: {
        'change input[name="delivery_type"]': '_alCambiarMetodoEntrega',
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'click .o_delivery_carrier_select': '_alCambiarMetodoEntrega', 
        'change #sucursal_select': '_alCambiarSucursal',
    },

    start: async function () {
        await this._super.apply(this, arguments);
        this._secuestrarBotonConfirmar();
        await this._cargarEstadoInicial();
        // Llamada rápida para pintar el selector si ya estaba seleccionado
        this._alCambiarMetodoEntrega();
    },

    // -------------------------------------------------------------------------
    // LÓGICA DE SECUESTRO (SOLUCIÓN FINAL)
    // -------------------------------------------------------------------------
    _secuestrarBotonConfirmar: function () {
        const self = this;
        const botonSelector = 'button[name="o_payment"], .o_sale_confirm, a[href*="/shop/confirm_order"]';

        $(document).on('click', botonSelector, async function (ev) {
            const $wrapper = $('#sucursal_picker_wrapper');
            
            // Solo intervenimos si el selector de sucursales es visible (es recogida)
            if ($wrapper.length && !$wrapper.hasClass('d-none')) {
                const valor = $('#sucursal_select').val();
                
                if (!valor) {
                    // BLOQUEO TOTAL si no hay sucursal
                    ev.preventDefault();
                    ev.stopImmediatePropagation();
                    alert("⚠️ Por favor selecciona una sucursal para recoger tu pedido.");
                    self._resaltarError();
                    return false; 
                }

                // Si hay valor, lo guardamos asíncronamente
                // NO usamos preventDefault aquí para que, tras el 'await', Odoo siga su flujo
                await rpc('/shop/update_sucursal', { sucursal: valor });
                
                // Al no haber preventDefault ni form.submit() manual, 
                // Odoo ejecutará sus validaciones de pago normales ahora que ya guardamos la sucursal.
            }
        });
    },
    // -------------------------------------------------------------------------
    // FUNCIONES AUXILIARES (Sin cambios)
    // -------------------------------------------------------------------------
    _alCambiarMetodoEntrega: async function () {
        const $checked = this.$('input[name="delivery_type"]:checked, input[name="o_delivery_radio"]:checked');
        if (!$checked.length) { this._ocultarSucursales(); return; }

        let carrier_id = $checked.val();
        if (carrier_id === 'on' || !parseInt(carrier_id)) {
             const inputId = $checked.attr('id');
             if (inputId) {
                 const match = inputId.match(/\d+$/);
                 if (match) carrier_id = match[0];
             }
        }
        
        const carrierIdInt = parseInt(carrier_id, 10);
        if (!carrierIdInt) return;

        if (await this._esMetodoRecogida(carrierIdInt)) {
            this._mostrarSucursales();
        } else {
            this._ocultarSucursales();
        }
    },

    _mostrarSucursales: function () {
        this.$('#sucursal_picker_wrapper').removeClass('d-none');
    },

    _ocultarSucursales: function () {
        this.$('#sucursal_picker_wrapper').addClass('d-none');
        this.$('#sucursal_select').val('');
        rpc('/shop/update_sucursal', { sucursal: "" }).catch(() => {});
    },

    _alCambiarSucursal: async function () {
        const valor = this.$('#sucursal_select').val();
        if(valor) this.$('#sucursal_select').removeClass('is-invalid');
        // Guardado silencioso de fondo
        rpc('/shop/update_sucursal', { sucursal: valor });
    },

    _resaltarError: function() {
        this.$('#sucursal_select').addClass('is-invalid');
        this.$('#sucursal_error_msg').removeClass('d-none').addClass('show');
        this.$('#sucursal_picker_wrapper')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    _esMetodoRecogida: async function (carrier_id) {
        if (!carrier_id) return false;
        try {
            const data = await rpc('/shop/es_recogida', { carrier_id: carrier_id });
            return data && data.es_recogida;
        } catch (error) { return false; }
    },

    _cargarEstadoInicial: async function () {
        try {
            const data = await rpc('/shop/get_sucursal', {});
            if (data && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
            }
        } catch (e) {}
    }
});

export default publicWidget.registry.SelectorSucursales;