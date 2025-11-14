/** @odoo-module **/

import { browser } from "@web/core/browser/browser";

const origURL = browser.location.href;

odoo.define("tu_modulo.url_patch", function (require) {
    "use strict";

    const oldPushState = window.history.pushState;

    window.history.pushState = function (state, title, url) {
        if (url && url.includes("/odoo")) {
            url = url.replace("/odoo", "/smarts");
        }
        return oldPushState.apply(this, [state, title, url]);
    };
});
