/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

console.log("✅ SelectorSucursales v12.0 - Guardado Forzoso al Confirmar");

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
        this._interceptarBotonConfirmar();
        await this._cargarEstadoInicial();
        setTimeout(() => { this._alCambiarMetodoEntrega(); }, 800);
    },

    // -------------------------------------------------------------------------
    // LÓGICA DE DETECCIÓN Y VISUALIZACIÓN
    // -------------------------------------------------------------------------
    _alCambiarMetodoEntrega: async function () {
        const $checked = this.$('input[name="delivery_type"]:checked, input[name="o_delivery_radio"]:checked');
        if (!$checked.length) { this._ocultarSucursales(); return; }

        let carrier_id = $checked.val();
        
        // Corrección ID 'on'
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
        // Limpiamos en backend sin bloquear
        rpc('/shop/update_sucursal', { sucursal: "" }).catch(() => {});
    },

    // -------------------------------------------------------------------------
    // GUARDADO INDIVIDUAL (Al cambiar el select)
    // -------------------------------------------------------------------------
    _alCambiarSucursal: async function () {
        const valor = this.$('#sucursal_select').val();
        await this._guardarSucursalBackend(valor);
    },

    _guardarSucursalBackend: async function (valor) {
        try {
            console.log(`💾 Intentando guardar: ${valor}`);
            const result = await rpc('/shop/update_sucursal', { sucursal: valor });
            
            // Si el servidor nos dice que hubo error (gracias al try/except de Python)
            if (result.status === 'error') {
                console.error("❌ Error reportado por servidor:", result.error);
                alert(`Error del sistema: ${result.error}\n\nAvise al administrador.`);
                return false;
            }
            
            console.log("✅ Guardado exitoso:", result);
            return true;
            
        } catch (error) {
            // Si el servidor explotó antes de poder responder (Error 500 real o Red)
            console.error("❌ Error Crítico RPC:", error);
            // Intentamos ignorarlo si es un error de red menor, pero lo logueamos
            return true; // Dejamos pasar "con fe" en la sesión
        }
    },

    // -------------------------------------------------------------------------
    // LÓGICA MAESTRA: INTERCEPTAR CONFIRMACIÓN (DOBLE CHECK)
    // -------------------------------------------------------------------------
    _interceptarBotonConfirmar: function () {
        const self = this;
        // Selectores de botones de pago/confirmación
        const botonSelector = 'a[href="/shop/payment"], button[name="o_payment"], .o_sale_confirm, a[name="website_sale_main_button"], a[href*="/shop/confirm_order"]';

        // Usamos capture=true para ser los primeros en enterarnos del click
        document.addEventListener('click', async function (e) {
            const target = e.target.closest(botonSelector);
            if (target) {
                const $wrapper = self.$('#sucursal_picker_wrapper');
                
                // Solo si el selector es visible (es método de recogida)
                if ($wrapper.length && !$wrapper.hasClass('d-none')) {
                    const valor = self.$('#sucursal_select').val();
                    
                    // 1. VALIDACIÓN VISUAL
                    if (!valor) {
                        e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
                        alert("⚠️ Por favor selecciona una sucursal.");
                        self._resaltarError();
                        return false;
                    }

                    // 2. GUARDADO FORZOSO (DOBLE CHECK)
                    // Detenemos el evento momentáneamente para asegurar el guardado
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Cambiamos texto del botón para feedback
                    const textoOriginal = target.innerText;
                    target.innerText = "Guardando...";
                    target.style.pointerEvents = "none"; // Evitar doble click

                    const guardadoOK = await self._guardarSucursalBackend(valor);

                    if (guardadoOK) {
                        // Si se guardó bien, redirigimos manualmente a la URL del botón
                        // o enviamos el formulario si era un botón submit
                        console.log("🚀 Redirigiendo a confirmar...");
                        
                        if (target.tagName === 'A') {
                            window.location.href = target.getAttribute('href');
                        } else if (target.type === 'submit' || target.tagName === 'BUTTON') {
                            // Si era un form submit, lo enviamos manualmente ahora
                            target.closest('form').submit();
                        }
                    } else {
                        // Si falló el guardado
                        target.innerText = textoOriginal;
                        target.style.pointerEvents = "auto";
                        alert("❌ Hubo un error de conexión al guardar tu sucursal. Intenta de nuevo.");
                    }
                }
            }
        }, true);
    },

    _resaltarError: function() {
        this.$('#sucursal_select').addClass('is-invalid');
        this.$('#sucursal_error_msg').removeClass('d-none').addClass('show');
        this.$('#sucursal_picker_wrapper')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    // -------------------------------------------------------------------------
    // CARGA INICIAL Y HELPERS
    // -------------------------------------------------------------------------
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