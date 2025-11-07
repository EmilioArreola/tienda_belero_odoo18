/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ Archivo sucursales_checkout.js ¡CARGADO! (v1.4 - con validación)");

/**
 * Widget para mostrar/ocultar selector de sucursales
 * en el checkout cuando se selecciona "Recoger en tienda"
 */
publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'click label.o_delivery_carrier_label': '_onClickDeliveryLabel',
        'change #sucursal_select': '_alCambiarSucursal',
        // Interceptar el submit del formulario para validar
        'submit form[name="checkout"]': '_onSubmitCheckout',
    },

    start: async function () {
        console.log("🚀 Widget SelectorSucursales INICIADO");
        this.rpc = this.bindService("rpc");

        await this._cargarEstadoInicial();

        return this._super.apply(this, arguments);
    },

    _cargarEstadoInicial: async function () {
        try {
            const data = await this.rpc('/shop/get_sucursal', {});

            if (data.status === 'success' && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
                console.log(`📥 Sucursal restaurada: ${data.sucursal}`);
            }

            // ... dentro de _cargarEstadoInicial o start ...
            setTimeout(() => {
                // Deseleccionar todos los radio buttons de entrega si ninguno está 'seleccionado'
                const $selectedRadio = this.$('input[name="o_delivery_radio"]:checked');
                if (!$selectedRadio.length) {
                    // Podrías intentar desmarcar todos para asegurar
                    this.$('input[name="o_delivery_radio"]').prop('checked', false);
                }
                this._alCambiarMetodoEntrega();
            }, 300);
            // ...

        } catch (error) {
            console.error("❌ Error al cargar estado inicial:", error);
            setTimeout(() => {
                this._alCambiarMetodoEntrega();
            }, 300);
        }
    },

    _onClickDeliveryLabel: function (ev) {
        setTimeout(() => {
            this._alCambiarMetodoEntrega();
        }, 50);
    },

    _alCambiarMetodoEntrega: function () {
        console.log("🖱️ Evento _alCambiarMetodoEntrega() disparado");

        const $radioSeleccionado = this.$('input[name="o_delivery_radio"]:checked');

        if (!$radioSeleccionado.length) {
            console.warn("⚠️ No se encontró ningún radio button seleccionado");
            this._ocultarSucursales();
            return;
        }

        const idRadio = $radioSeleccionado.attr('id');
        const $label = this.$('label[for="' + idRadio + '"]');
        const textoLabel = $label.text().trim().toLowerCase();
        const tipoEntrega = $radioSeleccionado.attr('data-delivery-type');
        const precio = parseFloat($radioSeleccionado.attr('data-amount') || 0);

        console.log("📝 Texto del label:", textoLabel);

        const esRecogerEnTienda = this._esMetodoRecogida(textoLabel, tipoEntrega, precio);

        if (esRecogerEnTienda) {
            console.log("✅ ES RECOGER EN TIENDA - Mostrando selector");
            this._mostrarSucursales();
        } else {
            console.log("👎 NO es recoger en tienda - Ocultando selector");
            this._ocultarSucursales();
        }
    },

    _esMetodoRecogida: function (textoLabel, tipoEntrega, precio) {
        const palabrasClave = ['recoger', 'tienda', 'sucursal', 'pickup', 'retirar'];
        const tienePalabraClave = palabrasClave.some(palabra => textoLabel.includes(palabra));
        const esFixedGratis = (tipoEntrega === 'fixed' && precio === 0);

        return tienePalabraClave || esFixedGratis;
    },

    _alCambiarSucursal: async function () {
        const $selector = this.$('#sucursal_select');
        $selector.removeClass('is-valid is-invalid'); // Añadir esta línea

        const valorSucursal = $selector.val();

        console.log(`🏦 Sucursal seleccionada: ${valorSucursal}`);

        $selector.prop('disabled', true);

        try {
            const data = await this.rpc('/shop/update_sucursal', {
                sucursal: valorSucursal
            });

            if (data.status === 'success') {
                console.log(`✅ Sucursal guardada: ${data.sucursal_guardada}`);
                $selector.removeClass('is-invalid').addClass('is-valid');
            } else {
                console.error(`❌ Error al guardar: ${data.error}`);
                $selector.addClass('is-invalid');
            }
        } catch (error) {
            console.error("❌ ERROR RPC:", error);
            $selector.addClass('is-invalid');
        } finally {
            $selector.prop('disabled', false);
        }
    },

    /**
     * Valida que se haya seleccionado una sucursal antes de enviar el formulario
     */
    _onSubmitCheckout: function (ev) {
        const $radioSeleccionado = this.$('input[name="o_delivery_radio"]:checked');
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');

        if ($radioSeleccionado.length) {
            const idRadio = $radioSeleccionado.attr('id');
            const $label = this.$('label[for="' + idRadio + '"]');
            const textoLabel = $label.text().trim().toLowerCase();
            const tipoEntrega = $radioSeleccionado.attr('data-delivery-type');
            const precio = parseFloat($radioSeleccionado.attr('data-amount') || 0);

            const esRecogerEnTienda = this._esMetodoRecogida(textoLabel, tipoEntrega, precio);

            // Validar si es método de recogida O si el contenedor está visible
            if (esRecogerEnTienda || !$contenedorSucursales.hasClass('d-none')) {
                const $selector = this.$('#sucursal_select');
                const valorSucursal = $selector.val();

                if (!valorSucursal || valorSucursal === '') {
                    ev.preventDefault();
                    ev.stopPropagation();

                    // Marcar el campo como inválido
                    $selector.addClass('is-invalid');
                    $contenedorSucursales.find('#sucursal_error_msg').removeClass('d-none'); // Mostrar mensaje de error

                    // Hacer scroll y mostrar alerta (como ya lo tienes)
                    $contenedorSucursales[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    alert('Por favor, seleccione una sucursal para recoger su pedido.');

                    console.warn("⚠️ Formulario bloqueado: No se ha seleccionado sucursal");
                    return false;
                } else {
                    // Si la validación es exitosa, asegúrate de quitar el mensaje de error
                    $selector.removeClass('is-invalid');
                    $contenedorSucursales.find('#sucursal_error_msg').addClass('d-none');
                }
            }
        }

        return true; // Continuar con el submit
    },


    _mostrarSucursales: function () {
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');

        if (!$contenedorSucursales.length) {
            console.error("❌ ERROR: No se encontró #sucursal_picker_wrapper");
            return;
        }

        $contenedorSucursales.removeClass('d-none').addClass('d-block');
        this.$('#sucursal_select').prop('required', true);

        const $select = this.$('#sucursal_select');
        if ($select.val() && $select.val() !== '') {
            this._alCambiarSucursal();
        }

        setTimeout(() => {
            $contenedorSucursales[0]?.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }, 100);
    },

    _ocultarSucursales: function () {
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');
        $contenedorSucursales.removeClass('d-block').addClass('d-none');

        const $select = this.$('#sucursal_select');
        $select.val('')
            .prop('required', false)
            .removeClass('is-valid is-invalid');

        this._alCambiarSucursal();
    },
});

export default publicWidget.registry.SelectorSucursales;