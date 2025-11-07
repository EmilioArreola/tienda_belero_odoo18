/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
// No necesitamos importar jsonrpc si usamos this.rpc bindeado

console.log("✅ Archivo sucursales_checkout.js ¡CARGADO! (v1.1)");

/**
 * Widget para mostrar/ocultar selector de sucursales
 * en el checkout cuando se selecciona "Recoger en tienda"
 */
publicWidget.registry.SelectorSucursales = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        // Evento específico para los radio buttons de Odoo
        'change input[name="o_delivery_radio"]': '_alCambiarMetodoEntrega',
        'click label.o_delivery_carrier_label': '_alCambiarMetodoEntrega',
        // NUEVO EVENTO: al cambiar la sucursal seleccionada
        'change #sucursal_select': '_alCambiarSucursal',
    },

    /**
     * @override
     */
    start: function () {
        console.log("🚀 Widget SelectorSucursales INICIADO");

        // Bindeamos el servicio RPC para poder llamar al controlador
        this.rpc = this.bindService("rpc");

        // Esperamos un poco para que el DOM esté completamente cargado
        setTimeout(() => {
            this._alCambiarMetodoEntrega();
        }, 300);

        return this._super.apply(this, arguments);
    },

    /**
     * Maneja el cambio de método de entrega
     * @private
     */
    _alCambiarMetodoEntrega: function () {
        console.log("🖱️ Evento _alCambiarMetodoEntrega() disparado");

        // Buscamos el radio button seleccionado
        const $radioSeleccionado = this.$('input[name="o_delivery_radio"]:checked');

        console.log("🔍 Total de métodos de envío (radio button) encontrados:", this.$('input[name="o_delivery_radio"]').length);
        console.log("🔍 Radio seleccionado:", $radioSeleccionado.length);

        if (!$radioSeleccionado.length) {
            console.warn("⚠️ No se encontró ningún radio button seleccionado");
            this._ocultarSucursales();
            return;
        }

        // Obtenemos el ID del delivery method
        const idMetodoEntrega = $radioSeleccionado.attr('data-dm-id');
        const tipoEntrega = $radioSeleccionado.attr('data-delivery-type');

        // Buscamos el label asociado
        const idRadio = $radioSeleccionado.attr('id');
        const $label = this.$('label[for="' + idRadio + '"]');
        const textoLabel = $label.text().trim().toLowerCase();

        console.log("🔵 ID del método:", idMetodoEntrega);
        console.log("🔵 Tipo de entrega:", tipoEntrega);
        console.log("📝 Texto del label:", textoLabel);

        // Verificamos si es "Recoger en tienda"
        // (Mejoramos un poco la lógica original)
        const esRecogerEnTienda = textoLabel.includes('recoger') ||
            textoLabel.includes('tienda') ||
            (tipoEntrega === 'fixed' && (textoLabel.includes('gratis') || textoLabel.includes('recoger')));

        if (esRecogerEnTienda) {
            console.log("✅ ¡ES RECOGER EN TIENDA! Mostrando selector de sucursales");
            this._mostrarSucursales();
            // Forzamos el envío de la sucursal actual (o la por defecto)
            this._alCambiarSucursal();
        } else {
            console.log("👎 NO es recoger en tienda. Ocultando selector de sucursales");
            this._ocultarSucursales();
        }
    },
    
    /**
     * NUEVA FUNCIÓN: Maneja el cambio en el selector de sucursal
     * y lo envía al backend
     * @private
     */
    _alCambiarSucursal: function () {
        const $selector = this.$('#sucursal_select');
        const valorSucursal = $selector.val();
        console.log(`🏦 Sucursal seleccionada: ${valorSucursal}`);

        // Usamos this.rpc (bindeado en start) para llamar a nuestra ruta JSON
        this.rpc('/shop/update_sucursal', {
            sucursal: valorSucursal
        }).then(function (data) {
            if (data.status === 'success') {
                console.log(`✅ Sucursal guardada en cotización: ${data.sucursal_guardada}`);
            } else {
                console.error(`❌ Error al guardar sucursal: ${data.error}`);
            }
        }).catch(function (error) {
            console.error("❌ ERROR RPC:", error);
        });
    },

    /**
     * Muestra el selector de sucursales
     * @private
     */
    _mostrarSucursales: function () {
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');

        if (!$contenedorSucursales.length) {
            console.error("❌ ERROR: No se encontró #sucursal_picker_wrapper");
            return;
        }

        $contenedorSucursales.removeClass('d-none').show();
        
        // Hacemos que el select sea requerido para la validación del form
        this.$('#sucursal_select').prop('required', true);

        // Hacer scroll suave hacia las sucursales
        setTimeout(() => {
            $contenedorSucursales[0].scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }, 100);
    },

    /**
     * Oculta el selector de sucursales
     * @private
     */
    _ocultarSucursales: function () {
        const $contenedorSucursales = this.$('#sucursal_picker_wrapper');
        $contenedorSucursales.addClass('d-none').hide();

        // Limpiar la selección y quitar 'required'
        this.$('#sucursal_select').val('').prop('required', false);
        
        // Enviar valor vacío al backend para limpiar la selección
        this._alCambiarSucursal(); 
    },
});

export default publicWidget.registry.SelectorSucursales;