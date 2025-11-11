/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ sucursales_checkout.js v3.0 - Validación completa en checkout");

publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'click label.o_delivery_carrier_label': '_onClickDeliveryLabel',
        'change #sucursal_select': '_alCambiarSucursal',
    },

    start: async function () {
        console.log("🚀 Widget iniciado");
        this.rpc = this.bindService("rpc");

        await this._cargarEstadoInicial();

        // Interceptor del botón "Continuar" del checkout
        this._interceptarBotonConfirmar();

        // Preseleccionar método de envío
        setTimeout(() => {
            console.log("Intentando preselección (con delay)...");
            this._preseleccionarEnvioPorDefecto();
            this._alCambiarMetodoEntrega();
        }, 300);

        return this._super.apply(this, arguments);
    },

    _preseleccionarEnvioPorDefecto: function () {
        const textoEnvio = "Envío (2-3 días hábiles)";
        const $labels = this.$('label.o_delivery_carrier_label');
        let found = false;

        this.$('input[name="o_delivery_radio"]:checked').prop('checked', false);
        console.log("Preselección de Odoo desmarcada.");

        $labels.each((i, label) => {
            const $label = $(label);
            const labelText = $label.text().trim().toLowerCase()
                .normalize("NFD").replace(/[\u0300-\u036f]/g, "");

            if (labelText.includes(textoEnvio)) {
                const radioId = $label.attr('for');
                if (radioId) {
                    const $radio = this.$('#' + radioId);
                    if ($radio.length) {
                        $radio.prop('checked', true);
                        console.log(`✅ Preselección aplicada: ${textoEnvio}`);
                        found = true;
                        return false;
                    }
                }
            }
        });

        if (!found) {
            console.warn(`⚠️ No se pudo preseleccionar el envío "${textoEnvio}"`);
        }
    },

    _cargarEstadoInicial: async function () {
        try {
            const data = await this.rpc('/shop/get_sucursal', {});
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

        // Botón "Continuar" en el checkout
        const botonSelector = 'a[href="/shop/payment"], button[name="o_payment"]';

        document.addEventListener('click', function (e) {
            const target = e.target.closest(botonSelector);
            if (target) {
                console.log("🛑 Click en botón 'Continuar' capturado");
                if (!self._validarSucursal()) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.warn("⛔ Bloqueado: No se seleccionó sucursal");
                    return false;
                } else {
                    console.log("✅ Validación OK — puede continuar");
                }
            }
        }, true);

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

    _onClickDeliveryLabel: function (ev) {
        setTimeout(() => {
            this._alCambiarMetodoEntrega();
        }, 100);
    },

    _alCambiarMetodoEntrega: function () {
        const $checked = this.$('input[name="o_delivery_radio"]:checked');
        if (!$checked.length) {
            this._ocultarSucursales();
            return;
        }

        const idRadio = $checked.attr('id');
        const $label = this.$('label[for="' + idRadio + '"]');

        // 🔹 LEEMOS EL NUEVO ATRIBUTO DEL XML
        // Esto será "true" o "false" (como string)
        const esRecogida = $checked.attr('data-es-recogida');

        console.log(`📝 Método: "${$label.text().trim()}" | Data Es Recogida: ${esRecogida}`);

        // 🔹 Pasamos el nuevo valor a nuestra función de lógica
        if (this._esMetodoRecogida(esRecogida)) {
            console.log("✅ Es recoger en tienda");
            this._mostrarSucursales();
        } else {
            console.log("❌ No es recoger en tienda");
            this._ocultarSucursales();
        }
    },

    _esMetodoRecogida: function (esRecogida) {
        // El atributo HTML será el string "true" si el campo booleano es True.
        // Cualquier otro valor ("false", undefined) se considerará falso.
        return esRecogida === "true";
    },

    _alCambiarSucursal: async function () {
        const $select = this.$('#sucursal_select');
        const valor = $select.val();
        console.log(`🏦 Sucursal cambiada a: "${valor}"`);

        $select.removeClass('is-invalid is-valid');
        this.$('#sucursal_error_msg').addClass('d-none').removeClass('show');

        $select.prop('disabled', true);
        try {
            const data = await this.rpc('/shop/update_sucursal', { sucursal: valor });
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

        this._alCambiarSucursal();
        this._actualizarEstadoBotonConfirmar();
    },
});

export default publicWidget.registry.SelectorSucursales;
