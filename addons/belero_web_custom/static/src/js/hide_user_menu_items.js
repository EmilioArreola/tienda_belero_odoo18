/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { UserMenu } from "@web/webclient/user_menu/user_menu";

patch(UserMenu.prototype, "hide_user_menu_items", {
    /**
     * Filtra los elementos del menú antes de mostrarlos.
     */
    async getElements() {
        const elements = await this._super(...arguments);
        // Filtramos los elementos que no queremos mostrar
        return elements.filter(
            (el) => !["documentation", "support", "about"].includes(el.id)
        );
    },
});
