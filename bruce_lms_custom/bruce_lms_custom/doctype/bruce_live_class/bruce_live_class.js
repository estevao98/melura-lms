frappe.ui.form.on("Bruce Live Class", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Abrir aula"), () => {
			const meetingUrl = get_meeting_url(frm);
			if (!meetingUrl) {
				show_missing_meeting_url();
				return;
			}

			window.open(meetingUrl, "_blank", "noopener");
		}, __("Jitsi"));

		frm.add_custom_button(__("Copiar link"), () => {
			const meetingUrl = get_meeting_url(frm);
			if (!meetingUrl) {
				show_missing_meeting_url();
				return;
			}

			copy_meeting_url(meetingUrl);
		}, __("Jitsi"));

		if (frm.doc.status === "Agendada") {
			frm.add_custom_button(__("Iniciar aula"), () => {
				frappe.call({
					method: "bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.start_live_class",
					args: {
						name: frm.doc.name,
					},
					freeze: true,
					freeze_message: __("Iniciando aula..."),
					callback(response) {
						const result = response.message || {};

						if (result.message) {
							frappe.show_alert({
								message: result.message,
								indicator: "green",
							});
						}

						frm.reload_doc();

						if (result.meeting_url) {
							window.open(result.meeting_url, "_blank", "noopener");
						}
					},
				});
			}, __("Jitsi")).addClass("btn-primary");
		}
	},
});

function get_meeting_url(frm) {
	return (frm.doc.meeting_url || "").trim();
}

function show_missing_meeting_url() {
	frappe.msgprint({
		title: __("Link da aula indisponível"),
		message: __("Esta aula ainda não tem link Jitsi. Salve a aula novamente ou revise a configuração do Jitsi."),
		indicator: "orange",
	});
}

function copy_meeting_url(meetingUrl) {
	if (frappe.utils && frappe.utils.copy_to_clipboard) {
		frappe.utils.copy_to_clipboard(meetingUrl);
		frappe.show_alert({
			message: __("Link da aula copiado."),
			indicator: "green",
		});
		return;
	}

	if (navigator.clipboard && window.isSecureContext) {
		navigator.clipboard.writeText(meetingUrl).then(() => {
			frappe.show_alert({
				message: __("Link da aula copiado."),
				indicator: "green",
			});
		}).catch(() => {
			show_manual_copy_dialog(meetingUrl);
		});
		return;
	}

	show_manual_copy_dialog(meetingUrl);
}

function show_manual_copy_dialog(meetingUrl) {
	frappe.msgprint({
		title: __("Copiar link da aula"),
		message: __("Não foi possível copiar automaticamente. Copie o link abaixo:") + `<br><br><code>${frappe.utils.escape_html(meetingUrl)}</code>`,
		indicator: "orange",
	});
}
