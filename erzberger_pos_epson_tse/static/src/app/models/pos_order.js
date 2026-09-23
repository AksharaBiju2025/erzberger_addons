import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { generateQRCodeSVG } from "../utils/qrcode_generator";

patch(PosOrder.prototype, {
    setup(vals = {}) {
        super.setup(...arguments);
        const v = vals || {};
        this.epson_tse_transaction_number = v.epson_tse_transaction_number || false;
        this.epson_tse_signature_counter = v.epson_tse_signature_counter || false;
        this.epson_tse_serial_number = v.epson_tse_serial_number || false;
        this.epson_tse_time_start = v.epson_tse_time_start || false;
        this.epson_tse_time_end = v.epson_tse_time_end || false;
        this.epson_tse_signature_value = v.epson_tse_signature_value || false;
        this.epson_tse_signature_algorithm = v.epson_tse_signature_algorithm || "ecdsa-plain-SHA256";
        this.epson_tse_public_key = v.epson_tse_public_key || false;
        this.epson_tse_qr_code = v.epson_tse_qr_code || false;
        this.epson_tse_status = v.epson_tse_status || "draft";
        this.epson_tse_qr_svg = v.epson_tse_qr_svg || (this.epson_tse_qr_code ? generateQRCodeSVG(this.epson_tse_qr_code, 140) : false);
    },


    get epsonTse() {
        if (!this.config?.l10n_de_epson_tse_enabled) {
            return false;
        }

        if (this.epson_tse_status === "signed") {
            const formatTime = (d) => {
                if (!d) return "";
                if (typeof d === "string") return d;
                return d.toISOString().replace("T", " ").substring(0, 19);
            };

            return {
                is_signed: true,
                is_test_mode: Boolean(this.config.l10n_de_epson_tse_test_mode),
                transaction_number: this.epson_tse_transaction_number,
                signature_counter: this.epson_tse_signature_counter,
                serial_number: this.epson_tse_serial_number || this.config.l10n_de_epson_tse_serial,
                time_start: formatTime(this.epson_tse_time_start),
                time_end: formatTime(this.epson_tse_time_end),
                signature_value: this.epson_tse_signature_value,
                signature_algorithm: this.epson_tse_signature_algorithm || "ecdsa-plain-SHA256",
                qr_svg: this.epson_tse_qr_svg || (this.epson_tse_qr_code ? generateQRCodeSVG(this.epson_tse_qr_code, 140) : false),
                qr_code: this.epson_tse_qr_code,
            };
        }

        return false;
    },

    serializeForORM(opts = {}) {
        const data = super.serializeForORM(...arguments);
        if (this.epson_tse_status && this.epson_tse_status !== "draft") {
            const formatToORM = (val) => {
                if (!val) return false;
                if (typeof val === "string") {
                    const d = new Date(val);
                    if (!isNaN(d.getTime())) {
                        return d.toISOString().replace("T", " ").substring(0, 19);
                    }
                    return val.replace("T", " ").substring(0, 19);
                }
                if (val && typeof val.toUTC === "function" && typeof val.toFormat === "function") {
                    return val.toUTC().toFormat("yyyy-MM-dd HH:mm:ss");
                }
                if (val instanceof Date) {
                    return val.toISOString().replace("T", " ").substring(0, 19);
                }
                return false;
            };

            data.epson_tse_status = this.epson_tse_status;
            data.epson_tse_transaction_number = this.epson_tse_transaction_number;
            data.epson_tse_signature_counter = this.epson_tse_signature_counter;
            data.epson_tse_serial_number = this.epson_tse_serial_number;
            data.epson_tse_time_start = formatToORM(this.epson_tse_time_start);
            data.epson_tse_time_end = formatToORM(this.epson_tse_time_end);
            data.epson_tse_signature_value = this.epson_tse_signature_value;
            data.epson_tse_signature_algorithm = this.epson_tse_signature_algorithm;
            data.epson_tse_public_key = this.epson_tse_public_key;
            data.epson_tse_qr_code = this.epson_tse_qr_code;
        }
        return data;
    },
});
