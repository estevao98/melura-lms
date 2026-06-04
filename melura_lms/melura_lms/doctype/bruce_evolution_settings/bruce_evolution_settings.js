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
				method: "melura_lms.services.whatsapp.test_evolution_configuration",
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

		frm.add_custom_button(__("Enviar mensagem de teste"), () => {
			if (frm.is_dirty()) {
				frappe.msgprint({
					title: __("Configuração não salva"),
					message: __("Salve as alterações antes de enviar uma mensagem de teste."),
					indicator: "orange",
				});
				return;
			}

			frappe.prompt(
				[
					{
						fieldname: "phone",
						fieldtype: "Data",
						label: __("Telefone WhatsApp"),
						reqd: 1,
						description: __("Informe apenas um telefone para este teste manual."),
					},
				],
				(values) => {
					frappe.confirm(
						__(
							"Enviar uma mensagem real de teste para {0}? Esta ação enviará somente uma mensagem.",
							[values.phone]
						),
						() => {
							frappe.call({
								method: "melura_lms.services.whatsapp.send_evolution_test_message",
								args: {
									phone: values.phone,
								},
								freeze: true,
								freeze_message: __("Enviando mensagem de teste..."),
								callback(response) {
									const result = response.message || {};

									frappe.msgprint({
										title: __("Mensagem de teste"),
										message: result.message || __("Não foi possível enviar a mensagem de teste."),
										indicator: result.sent ? "green" : "orange",
									});
								},
							});
						}
					);
				},
				__("Enviar mensagem de teste"),
				__("Enviar")
			);
		}, __("WhatsApp"));
	},
});
