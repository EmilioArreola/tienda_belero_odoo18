/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { UserMenu } from "@web/webclient/user_menu/user_menu";

patch(UserMenu, {
    
    async getElements() {
        const elements = await this._super(...arguments);
        
        // --- INICIO DE DEBUG ---
        // Esto imprimirá todos los elementos del menú en la consola
        // para que podamos ver sus IDs reales.
        console.log("ELEMENTOS DEL MENÚ DE USUARIO:", elements);
        // --- FIN DE DEBUG ---

        // Dejamos la lógica de filtrado original
        return elements.filter(
            (el) => !["documentation", "support", "about"].includes(el.id)
        );
    },
});