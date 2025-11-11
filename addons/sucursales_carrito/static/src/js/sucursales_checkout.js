/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("✅ sucursales_checkout.js v5.0 (Versión Limpia)");

publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap', // Se aplica a toda la página

    events: {
        // 1. EL ÚNICO evento para el cambio de envío
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        // 2. El evento para guardar la sucursal seleccionada
        'change #sucursal_select': '_alCambiarSucursal',
    },

    /**
     * @override
     * Se ejecuta al cargar la página
     */
    start: async function () {
        // Llamada obligatoria a super() para widgets async
        await this._super.apply(this, arguments);
        console.log("🚀 Widget v5.0 Iniciado");

        // 1. Activar el interceptor del botón "Confirmar"
        this._interceptarBotonConfirmar();

        // 2. Restaurar el estado de la sucursal (si el usuario recarga la página)
        await this._cargarEstadoInicial();

        // 3. Comprobar el estado inicial al cargar la página
        // (Esto soluciona el caso "precargado" que mencionaste)
        this._alCambiarMetodoEntrega();
    },

    //==============================================
    // LÓGICA DE MOSTRAR / OCULTAR
    //==============================================

    /**
     * Función PRINCIPAL. Se llama al cargar y al cambiar el envío.
     * Revisa el envío seleccionado y decide si muestra u oculta las sucursales.
     */
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

        // Preguntamos al backend (asíncrono)
        if (await this._esMetodoRecogida(carrier_id)) {
            console.log("✅ Es 'Recoger'. MOSTRANDO sucursales.");
            this._mostrarSucursales();
        } else {
            console.log("❌ No es 'Recoger'. OCULTANDO sucursales.");
            this._ocultarSucursales();
        }
    },

    /**
     * Muestra el contenedor de sucursales
     */
    _mostrarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        if (!$wrapper.length) return;

        $wrapper.removeClass('d-none').addClass('d-block');
        // Scroll suave
        $wrapper[0]?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    /**
     * Oculta el contenedor de sucursales
     */
    _ocultarSucursales: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');
        $wrapper.removeClass('d-block').addClass('d-none');

        // Limpia el select y los errores
        const $select = this.$('#sucursal_select');
        $select.val('').removeClass('is-valid is-invalid');
        this.$('#sucursal_error_msg').removeClass('show');

        // Limpiamos la sucursal guardada en el backend
        // Esta es la única llamada RPC "extra" que necesitamos.
        // Se "dispara y olvida" para limpiar el estado.
        this._rpc('/shop/update_sucursal', { sucursal: "" })
            .catch(err => console.error("Error limpiando sucursal:", err));
    },

    //==============================================
    // LÓGICA DE VALIDACIÓN Y GUARDADO
    //==============================================

    /**
     * Intercepta el clic en el botón "Confirmar"
     */
    _interceptarBotonConfirmar: function () {
        const self = this;
        const botonSelector = 'a[href="/shop/payment"], button[name="o_payment"]';

        // Usamos 'document' para capturar el clic
        document.addEventListener('click', function (e) {
            const target = e.target.closest(botonSelector);
            if (target) {
                console.log("🛑 Clic en 'Confirmar' capturado");

                // VALIDACIÓN 1: ¿Eligió método de entrega?
                if (!self._validarMetodoEntrega()) {
                    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
                    console.warn("⛔ BLOQUEADO: No hay método de entrega");
                    return false;
                }

                // VALIDACIÓN 2: ¿Eligió sucursal (si aplica)?
                if (!self._validarSucursal()) {
                    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
                    console.warn("⛔ BLOQUEADO: No se seleccionó sucursal");
                    return false;
                }

                console.log("✅ Validación OK — puede continuar");
            }
        }, true); // Usar 'true' (capturing) es importante

        console.log("✅ Interceptor de botón 'Confirmar' ACTIVO");
    },

    /**
     * VALIDADOR 1: Revisa si se seleccionó un método de entrega
     */
    _validarMetodoEntrega: function () {
        if (this.$('input[name="o_delivery_radio"]:checked').length === 0) {
            alert('⚠️ Por favor, seleccione un método de entrega antes de continuar.');
            // Hacemos scroll a la sección
            this.$('input[name="o_delivery_radio"]').first().closest('div.card-body, .o_delivery_carrier_select')[0]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
        return true;
    },

    /**
     * VALIDADOR 2: Revisa si se seleccionó una sucursal (SI ES REQUERIDO)
     */
    _validarSucursal: function () {
        const $wrapper = this.$('#sucursal_picker_wrapper');

        // Si el selector no está visible, no se requiere validación
        if (!$wrapper.length || $wrapper.hasClass('d-none')) {
            return true;
        }

        const $select = this.$('#sucursal_select');
        const valor = $select.val();

        // Si está visible Y el valor está vacío, es un error
        if (!valor || valor === '' || valor === null) {
            console.warn("⛔ Validación fallida: No hay sucursal seleccionada");
            $select.addClass('is-invalid').removeClass('is-valid');
            this.$('#sucursal_error_msg').removeClass('d-none').addClass('show');

            alert('⚠️ Por favor, seleccione una sucursal antes de continuar.');
            $wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }

        return true; // Validación OK
    },

    //==============================================
    // FUNCIONES HELPER (RPC)
    //==============================================

    /**
     * HELPER 1: Carga la sucursal guardada en la sesión al iniciar
     */
    _cargarEstadoInicial: async function () {
        try {
            const data = await this._rpc('/shop/get_sucursal', {});
            if (data.status === 'success' && data.sucursal) {
                this.$('#sucursal_select').val(data.sucursal);
                console.log(`📥 Sucursal restaurada: ${data.sucursal}`);
            }
        } catch (error) {
            console.error("❌ Error cargando estado inicial:", error);
        }
    },

    /**
     * HELPER 2: Guarda la sucursal seleccionada en la sesión
     */
    _alCambiarSucursal: async function () {
        const $select = this.$('#sucursal_select');
        const valor = $select.val();
        console.log(`🏦 Sucursal cambiada a: "${valor}"`);

        // Quitar errores
        $select.removeClass('is-invalid is-valid');
        this.$('#sucursal_error_msg').addClass('d-none').removeClass('show');

        $select.prop('disabled', true); // Bloquear mientras guarda
        try {
            const data = await this._rpc('/shop/update_sucursal', { sucursal: valor });
            if (data.status === 'success') {
                console.log(`✅ Sucursal guardada en backend`);
                if (valor && valor !== '') {
                    $select.addClass('is-valid'); // Feedback visual
                }
            }
        } catch (error) {
            console.error("❌ Error RPC en _alCambiarSucursal:", error);
            $select.addClass('is-invalid');
        } finally {
            $select.prop('disabled', false); // Desbloquear
        }
    },

    /**
     * HELPER 3: Pregunta al backend si un ID es de recogida
     */
    _esMetodoRecogida: async function (carrier_id) {
        if (!carrier_id) return false;
        try {
            const data = await this._rpc('/shop/es_recogida', { carrier_id: carrier_id });
            return data.es_recogida;
        } catch (error) {
            console.error("❌ Error RPC en _esMetodoRecogida:", error);
            return false;
        }
    },

});

export default publicWidget.registry.SelectorSucursales;