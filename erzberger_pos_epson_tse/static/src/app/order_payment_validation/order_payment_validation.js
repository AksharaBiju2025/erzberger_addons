import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import { patch } from "@web/core/utils/patch";

patch(OrderPaymentValidation.prototype, {
    async askBeforeValidation() {
        const canProceed = await super.askBeforeValidation(...arguments);
        if (!canProceed) {
            return false;
        }

        if (this.pos.config.l10n_de_epson_tse_enabled) {
            const epsonTse = this.pos.env.services.epson_tse;
            if (epsonTse) {
                const signed = await epsonTse.signOrder(this.order);
                if (!signed) {
                    return false;
                }
            }
        }

        return true;
    },
});
