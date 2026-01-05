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
        // Selectores de los botones que finalizan la compra
        const botonSelector = 'a[href="/shop/payment"], button[name="o_payment"], .o_sale_confirm, a[name="website_sale_main_button"], a[href*="/shop/confirm_order"]';

        // Usamos onClick en el documento para atraparlo antes que nadie
        document.addEventListener('click', async function (e) {
            const target = e.target.closest(botonSelector);
            if (!target) return;

            // 1. Verificamos si debemos intervenir (¿Es recogida?)
            const $wrapper = self.$('#sucursal_picker_wrapper');
            if (!$wrapper.length || $wrapper.hasClass('d-none')) {
                return; // No es recogida, dejamos que Odoo haga su trabajo
            }

            // 2. DETENEMOS TODO INMEDIATAMENTE
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();

            // 3. Validación Visual
            const valor = self.$('#sucursal_select').val();
            if (!valor) {
                alert("⚠️ Por favor selecciona una sucursal para recoger tu pedido.");
                self._resaltarError();
                return;
            }

            // 4. BLOQUEO VISUAL
            const $btn = $(target);
            const textoOriginal = $btn.text();
            $btn.text("Guardando y Procesando...").prop('disabled', true).addClass('disabled');

            try {
                // 5. GUARDADO CRÍTICO (Esperamos respuesta del servidor)
                console.log("⏳ Enviando sucursal:", valor);
                await rpc('/shop/update_sucursal', { sucursal: valor });
                console.log("✅ Servidor confirmó guardado. Cookie actualizada.");

                // 6. EJECUCIÓN MANUAL (Bypasseando JS de Odoo)
                // Aquí está el truco: No hacemos click, hacemos lo que el click haría.
                
                if (target.tagName === 'BUTTON' || target.type === 'submit') {
                    // Si es un botón, buscamos su formulario y lo enviamos NATIVAMENTE
                    const form = target.closest('form');
                    if (form) {
                        console.log("🚀 Enviando formulario nativamente...");
                        form.submit(); // Esto envía el form sin disparar validaciones JS de nuevo
                    } else {
                        console.error("No se encontró formulario para el botón");
                        window.location.reload(); // Fallback
                    }
                } else if (target.tagName === 'A' && target.href) {
                    // Si es un enlace, navegamos
                    console.log("🚀 Navegando a:", target.href);
                    window.location.href = target.href;
                }

            } catch (error) {
                console.error("❌ Error fatal:", error);
                $btn.text(textoOriginal).prop('disabled', false).removeClass('disabled');
                alert("Hubo un error de conexión. Intenta de nuevo.");
            }

        }, true); // 'true' = Capture Phase (Somos los primeros en enterarnos)
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