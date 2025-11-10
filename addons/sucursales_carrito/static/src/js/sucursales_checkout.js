/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ sucursales_checkout.js v2.1 - Con Preselección");

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

        // REQ 1: Preseleccionar el envío por defecto
        this._preseleccionarEnvioPorDefecto();

        await this._cargarEstadoInicial();

        // REQ 2: Interceptar botón
        this._interceptarBotonConfirmar();

        // Llamar a esto al final para ocultar el selector de sucursal
        // (ya que el envío preseleccionado NO es "recoger")
        setTimeout(() => {
            this._alCambiarMetodoEntrega();
        }, 100); // Dar un pequeño delay para asegurar que todo cargó

        return this._super.apply(this, arguments);
    },

    /**
     * NUEVA FUNCIÓN (REQ 1): Preseleccionar "Envío (2-3 días hábiles)"
     */
    _preseleccionarEnvioPorDefecto: function () {
        // Texto a buscar (en minúsculas y sin acentos para ser más robusto)
        const textoEnvio = "envio (2-3 dias habiles)";
        const $labels = this.$('label.o_delivery_carrier_label');
        let found = false;

        $labels.each((i, label) => {
            const $label = $(label);
            // Normalizar texto: quitar acentos, espacios extra y a minúsculas
            const labelText = $label.text().trim().toLowerCase()
                .normalize("NFD").replace(/[\u0300-\u036f]/g, "");

            if (labelText.includes(textoEnvio)) {
                const radioId = $label.attr('for');
                if (radioId) {
                    const $radio = this.$('#' + radioId);
                    if ($radio.length) {
                        // Desmarcar todos primero
                        this.$('input[name="o_delivery_radio"]').prop('checked', false);
                        // Marcar el correcto
                        $radio.prop('checked', true);
                        console.log(`✅ Preselección aplicada: ${textoEnvio}`);
                        found = true;
                        return false; // Salir del 'each'
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
            // Esta ruta la agregamos en controllers/main.py
            const data = await this.rpc('/shop/get_sucursal', {});

            if (data.status === 'success' && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
                console.log(`📥 Sucursal restaurada: ${data.sucursal}`);
            }
        } catch (error) {
            console.error("❌ Error inicial:", error);
        }
    },

    /**
     * REQ 2: Interceptar el botón Confirmar
     */
    _interceptarBotonConfirmar: function () {
        const self = this;
        const botonSelector = 'a[href="/shop/confirm_order"]';

        // Usar event delegation en un elemento estático superior
        // Esto es más robusto que $(selector).on('click'...)
        this.$el.on('click', botonSelector, function (ev) {
            console.log("🔴 BOTÓN CONFIRMAR CLICKEADO");

            const $wrapper = self.$('#sucursal_picker_wrapper');

            // Solo validar si las sucursales están visibles
            if ($wrapper.length > 0 && !$wrapper.hasClass('d-none')) {
                const $select = self.$('#sucursal_select');
                const valor = $select.val();

                console.log(`🔍 Validando sucursal: "${valor}"`);

                if (!valor || valor === '' || valor === null) {
                    // BLOQUEAR navegación
                    ev.preventDefault();
                    ev.stopPropagation();
                    ev.stopImmediatePropagation();

                    console.warn("⛔ BLOQUEADO - No hay sucursal");

                    // Marcar error
                    $select.addClass('is-invalid').removeClass('is-valid');
                    self.$('#sucursal_error_msg').addClass('show');

                    // Scroll
                    $wrapper[0].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });

                    // Alert
                    setTimeout(() => {
                        alert('⚠️ Por favor, seleccione una sucursal antes de continuar.');
                    }, 100);

                    return false;
                } else {
                    console.log("✅ Validación OK - Continuando");
                }
            }
        });

        console.log("✅ Interceptor de clic instalado");
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
        const texto = $label.text().trim().toLowerCase();
        const tipo = $checked.attr('data-delivery-type');
        const precio = parseFloat($checked.attr('data-amount') || 0);

        console.log(`📝 Método: "${texto}" | Tipo: ${tipo} | Precio: ${precio}`);

        if (this._esMetodoRecogida(texto, tipo, precio)) {
            console.log("✅ Es recoger en tienda");
            this._mostrarSucursales();
        } else {
            console.log("❌ No es recoger en tienda");
            this._ocultarSucursales();
        }
    },

    _esMetodoRecogida: function (texto, tipo, precio) {
        const palabras = ['recoger', 'tienda', 'sucursal', 'pickup', 'retirar'];
        const tienePalabra = palabras.some(p => texto.includes(p));
        const esGratis = (tipo === 'fixed' && precio === 0); // "Recoger en tienda" es gratis

        return tienePalabra || esGratis;
    },

    _alCambiarSucursal: async function () {
        const $select = this.$('#sucursal_select');
        const valor = $select.val();

        console.log(`🏦 Sucursal cambiada a: "${valor}"`);

        // Limpiar errores inmediatamente
        $select.removeClass('is-invalid is-valid');
        this.$('#sucursal_error_msg').removeClass('show');

        $select.prop('disabled', true);

        try {
            const data = await this.rpc('/shop/update_sucursal', {
                sucursal: valor
            });

            if (data.status === 'success') {
                console.log(`✅ Guardado en backend`);
                // Solo poner verde si hay valor válido
                if (valor && valor !== '') {
                    $select.addClass('is-valid');
                }
            }
        } catch (error) {
            console.error("❌ Error RPC:", error);
        } finally {
            $select.prop('disabled', false);
        }
    },

    _mostrarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        if (!$wrapper.length) { return; }

        $wrapper.removeClass('d-none').addClass('d-block');

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
        $select.val('')
            .removeClass('is-valid is-invalid');

        this.$('#sucursal_error_msg').removeClass('show');

        // Limpiar en backend
        this._alCambiarSucursal();
    },
});

export default publicWidget.registry.SelectorSucursales;