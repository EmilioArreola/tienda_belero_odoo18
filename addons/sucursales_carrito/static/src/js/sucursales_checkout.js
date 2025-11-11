/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
// ⬇️ 1. ¡ESTA ES LA IMPORTACIÓN CLAVE QUE FALTABA! ⬇️
import { jsonrpc } from "@web/core/network/rpc";

console.log("✅ sucursales_checkout.js v6.0 (usando jsonrpc)");

publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',

    events: {
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'change #sucursal_select': '_alCambiarSucursal',
    },

    /**
     * @override
     */
    start: async function () {
        await this._super.apply(this, arguments);
        console.log("🚀 Widget v6.0 Iniciado");

        this._interceptarBotonConfirmar();
        await this._cargarEstadoInicial();
        this._alCambiarMetodoEntrega();
    },

    //==============================================
    // LÓGICA DE MOSTRAR / OCULTAR
    //==============================================

    _alCambiarMetodoEntrega: async function () {
        console.log("🖱️ Revisando método de entrega...");
        const $checked = this.$('input[name="o_delivery_radio"]:checked');

        if (!$checked.length) {
            console.log("...ningún envío seleccionado. Ocultando.");
            this._ocultarSucursales();
            return;
        }

        const carrier_id = $checked.val();
        console.log(`...ID de envío: ${carrier_id}`);

        if (await this._esMetodoRecogida(carrier_id)) {
            console.log("✅ Es 'Recoger'. MOSTRANDO sucursales.");
            this._mostrarSucursales();
        } else {
            console.log("❌ No es 'Recoger'. OCULTANDO sucursales.");
            this._ocultarSucursales();
        }
    },

    _mostrarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        if (!$wrapper.length) return;

        $wrapper.removeClass('d-none').addClass('d-block');
        $wrapper[0]?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    _ocultarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        $wrapper.removeClass('d-block').addClass('d-none');

        const $select = this.$('#sucursal_select');
        $select.val('').removeClass('is-valid is-invalid');
        this.$('#sucursal_error_msg').removeClass('show');

        // ⬇️ 2. CAMBIADO DE this._rpc A jsonrpc ⬇️
        jsonrpc('/shop/update_sucursal', { sucursal: "" })
            .catch(err => console.error("Error limpiando sucursal:", err));
    },

    //==============================================
    // LÓGICA DE VALIDACIÓN Y GUARDADO
    //==============================================

    _interceptarBotonConfirmar: function () {
        // ... (Esta función estaba bien, no usa RPC) ...
        // (La omito aquí por brevedad, pero déjala como estaba)
        const self = this;
        const botonSelector = 'a[href="/shop/payment"], button[name="o_payment"]';

        document.addEventListener('click', function (e) {
            const target = e.target.closest(botonSelector);
            if (target) {
                console.log("🛑 Clic en 'Confirmar' capturado");

                if (!self._validarMetodoEntrega()) {
                    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
                    console.warn("⛔ BLOQUEADO: No hay método de entrega");
                    return false;
                }
                if (!self._validarSucursal()) {
                    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
                    console.warn("⛔ BLOQUEADO: No se seleccionó sucursal");
                    return false;
                }

                console.log("✅ Validación OK — puede continuar");
            }
        }, true);

        console.log("✅ Interceptor de botón 'Confirmar' ACTIVO");
    },

    _validarMetodoEntrega: function () {
        // ... (Esta función estaba bien, no usa RPC) ...
        // (La omito aquí por brevedad, pero déjala como estaba)
        if (this.$('input[name="o_delivery_radio"]:checked').length === 0) {
            alert('⚠️ Por favor, seleccione un método de entrega antes de continuar.');
            this.$('input[name="o_delivery_radio"]').first().closest('div.card-body, .o_delivery_carrier_select')[0]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
        return true;
    },

    _validarSucursal: function () {
        // ... (Esta función estaba bien, no usa RPC) ...
        // (La omito aquí por brevedad, pero déjala como estaba)
        const $wrapper = this.$('#sucursal_picker_wrapper');
        if (!$wrapper.length || $wrapper.hasClass('d-none')) {
            return true;
        }
        const $select = this.$('#sucursal_select');
        const valor = $select.val();
        if (!valor || valor === '' || valor === null) {
            console.warn("⛔ Validación fallida: No hay sucursal seleccionada");
            $select.addClass('is-invalid').removeClass('is-valid');
            this.$('#sucursal_error_msg').removeClass('d-none').addClass('show');
            alert('⚠️ Por favor, seleccione una sucursal antes de continuar.');
            $wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
        return true;
    },

    //==============================================
    // FUNCIONES HELPER (RPC)
    //==============================================

    _cargarEstadoInicial: async function () {
        try {
            // ⬇️ 2. CAMBIADO DE this._rpc A jsonrpc ⬇️
            const data = await jsonrpc('/shop/get_sucursal', {});
            if (data.status === 'success' && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
                console.log(`📥 Sucursal restaurada: ${data.sucursal}`);
            }
        } catch (error) {
            console.error("❌ Error cargando estado inicial:", error);
        }
    },

    _alCambiarSucursal: async function () {
        const $select = this.$('#sucursal_select');
        const valor = $select.val();
        console.log(`🏦 Sucursal cambiada a: "${valor}"`);

        $select.removeClass('is-invalid is-valid');
        this.$('#sucursal_error_msg').addClass('d-none').removeClass('show');
        $select.prop('disabled', true);

        try {
            // ⬇️ 2. CAMBIADO DE this._rpc A jsonrpc ⬇️
            const data = await jsonrpc('/shop/update_sucursal', { sucursal: valor });
            if (data.status === 'success') {
                console.log(`✅ Sucursal guardada en backend`);
                if (valor && valor !== '') {
                    $select.addClass('is-valid');
                }
            }
        } catch (error) {
            console.error("❌ Error RPC en _alCambiarSucursal:", error);
            $select.addClass('is-invalid');
        } finally {
            $select.prop('disabled', false);
        }
    },

    _esMetodoRecogida: async function (carrier_id) {
        if (!carrier_id) return false;
        try {
            // ⬇️ 2. CAMBIADO DE this._rpc A jsonrpc ⬇️
            const data = await jsonrpc('/shop/es_recogida', { carrier_id: carrier_id });
            return data.es_recogida;
        } catch (error) {
            console.error("❌ Error RPC en _esMetodoRecogida:", error);
            return false;
        }
    },

});

export default publicWidget.registry.SelectorSucursales;