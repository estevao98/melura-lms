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

		frm.add_custom_button(__("Enviar link por WhatsApp"), () => {
			frappe.call({
				method: "bruce_lms_custom.services.whatsapp.send_live_class_link",
				args: {
					live_class: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Enviando link por WhatsApp..."),
				callback(response) {
					const result = response.message || {};
					const indicator = result.status === "sent" ? "green" : "orange";

					frappe.show_alert({
						message: result.message || __("Solicitação de envio registrada."),
						indicator,
					});

					frm.reload_doc();
				},
			});
		}, __("WhatsApp"));

		frm.add_custom_button(__("Pré-visualizar WhatsApp"), () => {
			frappe.call({
				method: "bruce_lms_custom.services.whatsapp.preview_live_class_link",
				args: {
					live_class: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Montando pré-visualização..."),
				callback(response) {
					show_whatsapp_preview_dialog(response.message || {});
				},
			});
		}, __("WhatsApp"));
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

function show_whatsapp_preview_dialog(result) {
	const recipients = result.recipients || [];
	const recipientRows = recipients.length
		? recipients.map((recipient) => `
			<tr>
				<td>${escape_html(recipient.recipient_name || __("Destinatário não informado"))}</td>
				<td>${escape_html(recipient.phone || __("Não informado"))}</td>
			</tr>
		`).join("")
		: `<tr><td colspan="2">${escape_html(__("Nenhum destinatário encontrado para esta aula."))}</td></tr>`;
	const warning = result.integration_warning
		? `<div class="alert alert-warning" style="margin-bottom: 12px;">${escape_html(result.integration_warning)}</div>`
		: "";
	const message = escape_html(result.message || "");

	const dialog = new frappe.ui.Dialog({
		title: __("Pré-visualizar WhatsApp"),
		size: "large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "preview",
				options: `
					${warning}
					<p><strong>${escape_html(__("Quantidade de destinatários"))}:</strong> ${Number(result.recipient_count || 0)}</p>
					<div style="max-height: 220px; overflow: auto; margin-bottom: 16px;">
						<table class="table table-bordered">
							<thead>
								<tr>
									<th>${escape_html(__("Nome"))}</th>
									<th>${escape_html(__("Telefone"))}</th>
								</tr>
							</thead>
							<tbody>${recipientRows}</tbody>
						</table>
					</div>
					<p><strong>${escape_html(__("Texto final da mensagem"))}</strong></p>
					<textarea class="form-control" readonly rows="8" style="resize: vertical;">${message}</textarea>
				`,
			},
		],
		primary_action_label: __("Fechar"),
		primary_action() {
			dialog.hide();
		},
	});

	dialog.show();
}

function escape_html(value) {
	if (frappe.utils && frappe.utils.escape_html) {
		return frappe.utils.escape_html(String(value || ""));
	}

	return String(value || "")
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}
