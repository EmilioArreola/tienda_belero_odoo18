/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ShareLinkCopy = publicWidget.Widget.extend({
    selector: '.s_share',
    
    events: {
        'click .fa-share-alt': '_onShareClick',
    },

    start: function () {
        // Mejora visual: Forzamos el cursor de mano sobre el ícono
        var $icon = this.$('.fa-share-alt');
        if ($icon.length) {
            $icon.css('cursor', 'pointer');
            $icon.attr('title', 'Copiar enlace al portapapeles');
        }
        return this._super.apply(this, arguments);
    },

    _onShareClick: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        
        var $icon = $(ev.currentTarget);
        var url = window.location.href;
        
        // Copiar al portapapeles
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(url).then(function() {
                // --- Feedback Visual (Palomita Verde) ---
                var originalClass = $icon.attr('class');
                
                $icon.removeClass('fa-share-alt').addClass('fa-check text-success');
                
                setTimeout(function() {
                    $icon.attr('class', originalClass);
                }, 2000);
            }).catch(function() {
                // Silencioso en caso de error
            });
        } else {
            // Fallback simple si no hay soporte seguro
            window.prompt("Copia el enlace:", url);
        }
    }
});