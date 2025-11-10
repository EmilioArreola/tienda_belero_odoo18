/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ sucursales_checkout.js v2.0 - DEFINITIVO");

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

        // Quitar preselección si existe
        this._quitarPreseleccion();

        await this._cargarEstadoInicial();
        this._interceptarBotonConfirmar();

        return this._super.apply(this, arguments);
    },

    /**
     * SOLUCIÓN 1: Quitar preselección de métodos de entrega
     */
    _quitarPreseleccion: function () {
        // Desmarcar todos los radio buttons al cargar
        this.$('input[name="o_delivery_radio"]').prop('checked', false);
        console.log("✅ Preselección removida");
    },

    _cargarEstadoInicial: async function () {
        try {
            const data = await this.rpc('/shop/get_sucursal', {});

            if (data.status === 'success' && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
                console.log(`📥 Sucursal restaurada: ${data.sucursal}`);
            }

            // Solo verificar método si hay uno seleccionado
            setTimeout(() => {
                const $checked = this.$('input[name="o_delivery_radio"]:checked');
                if ($checked.length > 0) {
                    this._alCambiarMetodoEntrega();
                }
            }, 300);

        } catch (error) {
            console.error("❌ Error inicial:", error);
        }
    },

    /**
     * SOLUCIÓN 3: Interceptar el botón Confirmar
     */
    _interceptarBotonConfirmar: function () {
        const self = this;

        // Interceptar TODOS los posibles botones de confirmar
        const selectores = [
            'a.website_sale_main_button[href="/shop/confirm_order"]',
            'a[href="/shop/confirm_order"]',
            'button.website_sale_main_button',
            'a:contains("Confirmar")',
        ];

        selectores.forEach(selector => {
            this.$(selector).on('click', function (ev) {
                console.log("🔴 BOTÓN CONFIRMAR CLICKEADO");

                const $wrapper = self.$('#sucursal_picker_wrapper');

                // Solo validar si las sucursales están visibles
                if (!$wrapper.hasClass('d-none')) {
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
        });

        // También interceptar por clase directamente
        document.addEventListener('click', function (e) {
            const target = e.target.closest('a[href="/shop/confirm_order"]');
            if (target) {
                console.log("🔴 Click detectado vía addEventListener");

                const $wrapper = self.$('#sucursal_picker_wrapper');
                if (!$wrapper.hasClass('d-none')) {
                    const $select = self.$('#sucursal_select');
                    const valor = $select.val();

                    if (!valor || valor === '') {
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();

                        $select.addClass('is-invalid');
                        self.$('#sucursal_error_msg').addClass('show');

                        alert('⚠️ Por favor, seleccione una sucursal.');
                        return false;
                    }
                }
            }
        }, true); // Usar capture phase

        console.log("✅ Interceptores instalados");
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
        const esGratis = (tipo === 'fixed' && precio === 0);

        return tienePalabra || esGratis;
    },

    /**
     * SOLUCIÓN 2: No mostrar error en rojo al seleccionar
     */
    _alCambiarSucursal: async function () {
        const $select = this.$('#sucursal_select');
        const valor = $select.val();

        console.log(`🏦 Sucursal cambiada a: "${valor}"`);

        // IMPORTANTE: Limpiar errores inmediatamente
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

        if (!$wrapper.length) {
            console.error("❌ No existe #sucursal_picker_wrapper");
            return;
        }

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