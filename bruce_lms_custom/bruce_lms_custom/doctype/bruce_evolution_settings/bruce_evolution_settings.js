frappe.ui.form.on("Bruce Evolution Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Testar configuração"), () => {
			if (frm.is_dirty()) {
				frappe.msgprint({
					title: __("Configuração não salva"),
					message: __("Salve as alterações antes de testar a configuração da Evolution API."),
					indicator: "orange",
				});
				return;
			}

			frappe.call({
				method: "bruce_lms_custom.services.whatsapp.test_evolution_configuration",
				freeze: true,
				freeze_message: __("Testando configuração..."),
				callback(response) {
					const result = response.message || {};

					frappe.msgprint({
						title: __("Teste da Evolution API"),
						message: result.message || __("Não foi possível validar a configuração."),
						indicator: result.valid ? "green" : "orange",
					});
				},
			});
		}, __("WhatsApp"));
	},
});
