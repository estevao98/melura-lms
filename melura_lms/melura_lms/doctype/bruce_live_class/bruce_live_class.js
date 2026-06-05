frappe.ui.form.on("Bruce Live Class", {
	refresh(frm) {
		set_live_class_form_title(frm);

		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Abrir aula"), () => {
			const meetingUrl = get_meeting_url(frm);
			if (!meetingUrl) {
				show_missing_meeting_url();
				return;
			}

			record_notice_event(frm.doc.name, "Aula aberta", __("Aula aberta"), __("A aula foi aberta pelo usuário no LMS."), "Sucesso", () => {
				render_notice_history(frm);
			});
			open_live_room(frm.doc.name);
		}, __("Aula ao vivo"));

		frm.add_custom_button(__("Copiar link"), () => {
			const meetingUrl = get_meeting_url(frm);
			if (!meetingUrl) {
				show_missing_meeting_url();
				return;
			}

			copy_meeting_url(frm, meetingUrl);
		}, __("Aula ao vivo"));

		if (frm.doc.status === "Agendada") {
			frm.add_custom_button(__("Iniciar aula"), () => {
				frappe.call({
					method: "melura_lms.melura_lms.doctype.bruce_live_class.bruce_live_class.start_live_class",
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

						if (result.name) {
							open_live_room(result.name);
						}
					},
				});
			}, __("Aula ao vivo")).addClass("btn-primary");
		}

		frm.add_custom_button(__("Enviar aviso aos alunos"), () => {
			frappe.call({
				method: "melura_lms.services.whatsapp.send_live_class_link",
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

		frm.add_custom_button(__("Enviar lembrete ao professor"), () => {
			frappe.call({
				method: "melura_lms.services.live_class_automation.send_professor_reminder_for_live_class",
				args: {
					live_class: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Enviando lembrete ao professor..."),
				callback(response) {
					const result = response.message || {};
					frappe.show_alert({
						message: result.sent ? __("Lembrete enviado ao professor.") : __("Não foi possível enviar o lembrete ao professor."),
						indicator: result.sent ? "green" : "orange",
					});
					frm.reload_doc();
				},
			});
		}, __("WhatsApp"));

		frm.add_custom_button(__("Pré-visualizar WhatsApp"), () => {
			frappe.call({
				method: "melura_lms.services.whatsapp.preview_live_class_link",
				args: {
					live_class: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Montando pré-visualização..."),
				callback(response) {
					show_whatsapp_preview_dialog(response.message || {});
					render_notice_history(frm);
				},
			});
		}, __("WhatsApp"));

		render_notice_history(frm);
	},
});

function set_live_class_form_title(frm) {
	if (!frm.page || !frm.page.set_title) {
		return;
	}

	const title = frm.is_new()
		? __("Nova aula ao vivo")
		: frm.doc.title || frm.doc.name || __("Aula ao vivo");
	frm.page.set_title(title);
}

function get_meeting_url(frm) {
	return (frm.doc.meeting_url || "").trim();
}

function open_live_room(liveClass) {
	frappe.set_route("melura-live-room", liveClass);
}

function show_missing_meeting_url() {
	frappe.msgprint({
		title: __("Link da aula indisponível"),
		message: __("Esta aula ainda não tem link do Google Meet configurado."),
		indicator: "orange",
	});
}

function copy_meeting_url(frm, meetingUrl) {
	if (frappe.utils && frappe.utils.copy_to_clipboard) {
		frappe.utils.copy_to_clipboard(meetingUrl);
		frappe.show_alert({
			message: __("Link da aula copiado."),
			indicator: "green",
		});
		record_notice_event(frm.doc.name, "Link copiado", __("Link da aula copiado"), __("O link da aula foi copiado pelo usuário."), "Sucesso", () => {
			render_notice_history(frm);
		});
		return;
	}

	if (navigator.clipboard && window.isSecureContext) {
		navigator.clipboard.writeText(meetingUrl).then(() => {
			frappe.show_alert({
				message: __("Link da aula copiado."),
				indicator: "green",
			});
			record_notice_event(frm.doc.name, "Link copiado", __("Link da aula copiado"), __("O link da aula foi copiado pelo usuário."), "Sucesso", () => {
				render_notice_history(frm);
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

function render_notice_history(frm) {
	if (!frm.fields_dict.notice_history_html) {
		return;
	}

	frappe.call({
		method: "melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.get_live_class_notice_logs",
		args: {
			live_class: frm.doc.name,
			limit: 6,
		},
		callback(response) {
			const logs = response.message || [];
			frm.set_df_property("notice_history_html", "options", build_notice_history_html(logs));
		},
	});
}

function build_notice_history_html(logs) {
	if (!logs.length) {
		return `<p class="text-muted">${escape_html(__("Nenhum aviso ou ação registrado para esta aula."))}</p>`;
	}

	const rows = logs.map((log) => `
		<tr>
			<td>${escape_html(format_datetime(log.created_at))}</td>
			<td>${escape_html(log.title || log.event_type || "")}</td>
			<td>${escape_html(log.status || "")}</td>
			<td>${escape_html(log.created_by || "")}</td>
		</tr>
	`).join("");

	return `
		<div style="max-height: 240px; overflow: auto;">
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>${escape_html(__("Data"))}</th>
						<th>${escape_html(__("Ação"))}</th>
						<th>${escape_html(__("Status"))}</th>
						<th>${escape_html(__("Usuário"))}</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		</div>
	`;
}

function record_notice_event(liveClass, eventType, title, message, status, callback) {
	frappe.call({
		method: "melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.record_live_class_notice_event",
		args: {
			live_class: liveClass,
			event_type: eventType,
			title,
			message,
			status,
		},
		callback() {
			if (callback) {
				callback();
			}
		},
	});
}

function format_datetime(value) {
	if (!value) {
		return "";
	}

	return frappe.datetime.str_to_user(value);
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
