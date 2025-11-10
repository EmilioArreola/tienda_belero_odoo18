/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ sucursales_checkout.js v2.2 - Corrección de Preselección y Validación");

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

        // REQ 2: Interceptar botón (Restaurado con doble seguro)
        this._interceptarBotonConfirmar();

        // REQ 1: Preseleccionar con delay para ganar a Odoo
        setTimeout(() => {
            console.log("Intentando preselección (con delay)...");
            this._preseleccionarEnvioPorDefecto();
            // Correr esto DESPUÉS de forzar la preselección
            this._alCambiarMetodoEntrega();
        }, 300); // Dar 300ms a Odoo para que cargue su default

        return this._super.apply(this, arguments);
    },

    /**
     * CORREGIDO (REQ 1): 
     * Ahora desmarca explícitamente cualquier radio que Odoo haya
     * preseleccionado (como "Recoger en tienda") ANTES de
     * marcar el nuestro.
     */
    _preseleccionarEnvioPorDefecto: function () {
        const textoEnvio = "envio (2-3 dias habiles)";
        const $labels = this.$('label.o_delivery_carrier_label');
        let found = false;

        // ¡CORRECCIÓN! Desmarcar explícitamente el radio ya seleccionado
        this.$('input[name="o_delivery_radio"]:checked').prop('checked', false);
        console.log("Preselección de Odoo (Recoger) desmarcada.");

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
     * CORREGIDO (REQ 2): 
     * Se restaura el 'EventListener' en modo 'capture' (true).
     * Esto es más agresivo y captura el clic ANTES de que Odoo
     * procese el 'href' del enlace.
     */
    _interceptarBotonConfirmar: function () {
        const self = this;
        const botonSelector = 'a[href="/shop/confirm_order"]';

        // SEGURO 1: (El que tenías en v2.0)
        // Este es el más importante. Se ejecuta en la fase de "captura".
        document.addEventListener('click', function (e) {
            // Usamos .closest() para ver si el clic fue en el botón o en un hijo
            const target = e.target.closest(botonSelector);
            if (target) {
                console.log("🔴 Clic capturado por addEventListener (fase capture)");
                if (self._validarSucursal()) {
                    // Si la validación pasa, permite el clic
                    console.log("✅ Validación OK (EventListener)");
                    return true;
                } else {
                    // Si la validación falla, bloquea el evento
                    console.warn("⛔ BLOQUEADO por addEventListener");
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    return false;
                }
            }
        }, true); // El 'true' es la clave, se ejecuta en fase de captura

        // SEGURO 2: (El de Odoo)
        // Por si acaso, dejamos también el listener de Odoo.
        this.$el.on('click', botonSelector, function (ev) {
            console.log("🔴 Clic capturado por Odoo .on()");
            if (!self._validarSucursal()) {
                console.warn("⛔ BLOQUEADO por Odoo .on()");
                ev.preventDefault();
                ev.stopPropagation();
                ev.stopImmediatePropagation();
            } else {
                console.log("✅ Validación OK (Odoo .on())");
            }
        });

        console.log("✅ Interceptores (Doble) instalados");
    },

    /**
     * Nueva función de apoyo para validar (y evitar repetir código)
     */
    _validarSucursal: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');

        // Si el wrapper no está visible, no hay nada que validar.
        if (!$wrapper.length || $wrapper.hasClass('d-none')) {
            return true; // Es válido continuar
        }

        // Si el wrapper SÍ está visible, validamos el select
        const $select = this.$('#sucursal_select');
        const valor = $select.val();

        if (!valor || valor === '' || valor === null) {
            // --- Validación FALLIDA ---
            console.warn("⛔ Validación fallida: No hay sucursal seleccionada");

            // Marcar error
            $select.addClass('is-invalid').removeClass('is-valid');
            this.$('#sucursal_error_msg').addClass('show');

            // Scroll
            $wrapper[0].scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // Alert
            setTimeout(() => {
                alert('⚠️ Por favor, seleccione una sucursal antes de continuar.');
            }, 100);

            return false; // Inválido
        }

        // --- Validación EXITOSA ---
        return true; // Es válido continuar
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

    _alCambiarSucursal: async function () {
        const $select = this.$('#sucursal_select');
        const valor = $select.val();
        console.log(`🏦 Sucursal cambiada a: "${valor}"`);

        // Limpiar errores en cuanto el usuario cambia la selección
        $select.removeClass('is-invalid is-valid');
        this.$('#sucursal_error_msg').removeClass('show');

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
        $select.val('').removeClass('is-valid is-invalid');
        this.$('#sucursal_error_msg').removeClass('show');

        this._alCambiarSucursal(); // Limpiar en backend
    },
});

export default publicWidget.registry.SelectorSucursales;