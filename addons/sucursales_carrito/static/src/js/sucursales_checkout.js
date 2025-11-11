/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ sucursales_checkout.js v3.0 - Validación completa en checkout");

publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'change #sucursal_select': '_alCambiarSucursal',
    },

    start: async function () {
        // ⬇️ ESTA ES LA CORRECCIÓN ⬇️
        // 1. Llama a 'super' PRIMERO y usa 'await'
        await this._super.apply(this, arguments);

        console.log("🚀 Widget iniciado");

        // 2. Ahora sí, ejecuta el resto de tu lógica async
        await this._cargarEstadoInicial();
        this._interceptarBotonConfirmar();

    },

    _cargarEstadoInicial: async function () {
        try {
            const data = await this._rpc('/shop/get_sucursal', {});
            if (data.status === 'success' && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
                console.log(`📥 Sucursal restaurada: ${data.sucursal}`);
            }
        } catch (error) {
            console.error("❌ Error inicial:", error);
        }
    },

    // ✅ Interceptor actualizado para el botón "Continuar" del checkout
    _interceptarBotonConfirmar: function () {
        const self = this;
        // El selector del botón está perfecto
        const botonSelector = 'a[href="/shop/payment"], button[name="o_payment"]';

        document.addEventListener('click', function (e) {
            const target = e.target.closest(botonSelector);
            if (target) {
                console.log("🛑 Click en botón 'Continuar' capturado");

                // 1️⃣ PRIMERA VALIDACIÓN: ¿Eligió método de entrega?
                if (!self._validarMetodoEntrega()) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.warn("⛔ Bloqueado: No se seleccionó método de entrega");
                    return false;
                }

                // 2️⃣ SEGUNDA VALIDACIÓN: ¿Eligió sucursal (si aplica)?
                if (!self._validarSucursal()) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.warn("⛔ Bloqueado: No se seleccionó sucursal");
                    return false;
                }

                // Si pasa ambas...
                console.log("✅ Validación OK — puede continuar");
            }
        }, true); // El 'true' (capturing) es importante, déjalo.

        console.log("✅ Interceptor activo para botón 'Continuar' en checkout");
    },

    _validarSucursal: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');

        if (!$wrapper.length || $wrapper.hasClass('d-none')) {
            return true; // No se requiere validación
        }

        const $select = this.$('#sucursal_select');
        const valor = $select.val();

        if (!valor || valor === '' || valor === null) {
            console.warn("⛔ Validación fallida: No hay sucursal seleccionada");

            $select.addClass('is-invalid').removeClass('is-valid');
            this.$('#sucursal_error_msg').removeClass('d-none').addClass('show');

            $wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });

            setTimeout(() => {
                alert('⚠️ Por favor, seleccione una sucursal antes de continuar.');
            }, 100);

            return false;
        }

        return true;
    },

    _validarMetodoEntrega: function () {
        const $checked = this.$('input[name="o_delivery_radio"]:checked');

        if ($checked.length === 0) {
            console.warn("⛔ Validación fallida: No hay método de entrega");

            // Hacemos scroll hacia la sección de métodos de entrega
            const $wrapper = this.$('input[name="o_delivery_radio"]').first().closest('div.card-body, .o_delivery_carrier_select');

            $wrapper[0]?.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // Mostramos una alerta
            setTimeout(() => {
                alert('⚠️ Por favor, seleccione un método de entrega antes de continuar.');
            }, 100);

            return false; // Bloquea
        }

        return true; // Permite
    },

    _alCambiarMetodoEntrega: async function () {
        const $checked = this.$('input[name="o_delivery_radio"]:checked');
        if (!$checked.length) {
            this._ocultarSucursales();
            return;
        }

        const idRadio = $checked.attr('id');
        const $label = this.$('label[for="' + idRadio + '"]');

        // 🔹 OBTENEMOS EL ID DEL MÉTODO DE ENVÍO
        // El valor del input radio es el ID del delivery.carrier
        const carrier_id = $checked.val();

        console.log(`📝 Método: "${$label.text().trim()}" | ID: ${carrier_id}`);

        // 🔹 PREGUNTAMOS AL SERVIDOR SI ES RECOGIDA
        if (await this._esMetodoRecogida(carrier_id)) {
            console.log("✅ Es recoger en tienda");
            this._mostrarSucursales();
        } else {
            console.log("❌ No es recoger en tienda");
            this._ocultarSucursales();
        }
    },

    _esMetodoRecogida: async function (carrier_id) {
        if (!carrier_id) {
            return false;
        }

        try {
            // 🔹 Llamamos a la nueva ruta del controlador
            const data = await this._rpc('/shop/es_recogida', {
                carrier_id: carrier_id
            });

            // Devolvemos la respuesta del servidor (true o false)
            return data.es_recogida;

        } catch (error) {
            console.error("❌ Error RPC al verificar método de recogida:", error);
            return false; // Asumimos falso si hay un error
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
            const data = await this._rpc('/shop/update_sucursal', { sucursal: valor });
            if (data.status === 'success') {
                console.log(`✅ Guardado en backend`);
                if (valor && valor !== '') {
                    $select.addClass('is-valid');
                }
            }
        } catch (error) {
            console.error("❌ Error RPC:", error);
        } finally {
            $select.prop('disabled', false);
            this._actualizarEstadoBotonConfirmar();
        }
    },

    _limpiarSucursalEnBackend: function () {
        console.log("🧹 Limpiando sucursal en backend...");

        // Esta función llama al backend para poner la sucursal en 'False'
        // pero NO es 'async' a propósito, para evitar "race conditions".
        // Simplemente "dispara y olvida".
        this._rpc('/shop/update_sucursal', { sucursal: "" })
            .then(data => {
                if (data.status === 'success') {
                    console.log(`✅ Sucursal limpiada en backend`);
                }
            })
            .catch(error => {
                console.error("❌ Error RPC al limpiar sucursal:", error);
            });
    },

    _actualizarEstadoBotonConfirmar: function () {
        // 🔹 Cambiado para buscar el botón "Continuar" del checkout
        const $boton = this.$('a[href="/shop/payment"], button[name="o_payment"]');
        const $wrapper = this.$('#sucursal_picker_wrapper');
        const $select = this.$('#sucursal_select');
        const $errorMsg = this.$('#sucursal_error_msg');

        if (!$wrapper.length || $wrapper.hasClass('d-none')) {
            $boton.removeAttr('disabled');
            $errorMsg.addClass('d-none');
            return;
        }

        const valor = $select.val();
        if (!valor || valor === '') {
            $boton.attr('disabled', true);
            $errorMsg.removeClass('d-none');
        } else {
            $boton.removeAttr('disabled');
            $errorMsg.addClass('d-none');
        }
    },

    _mostrarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        if (!$wrapper.length) return;

        $wrapper.removeClass('d-none').addClass('d-block');
        this._actualizarEstadoBotonConfirmar();

        const $select = this.$('#sucursal_select');
        const valorActual = $select.val();
        if (valorActual && valorActual !== '') {
            this._alCambiarSucursal();
        }

        setTimeout(() => {
            $wrapper[0]?.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }, 150);
    },

    _ocultarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        $wrapper.removeClass('d-block').addClass('d-none');

        const $select = this.$('#sucursal_select');
        $select.val('').removeClass('is-valid is-invalid');
        this.$('#sucursal_error_msg').removeClass('show');

        // ✅ REEMPLAZAMOS LA LÍNEA MALA POR LA NUEVA FUNCIÓN:
        this._limpiarSucursalEnBackend();

        this._actualizarEstadoBotonConfirmar();
    },
});

export default publicWidget.registry.SelectorSucursales;
