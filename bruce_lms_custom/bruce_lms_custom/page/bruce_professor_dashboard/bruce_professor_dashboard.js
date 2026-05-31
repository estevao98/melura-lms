frappe.pages["bruce-professor-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel do Professor"),
		single_column: true,
	});

	page.main.addClass("bruce-professor-dashboard");
	const dashboard = new BruceProfessorDashboard(page);

	page.set_primary_action(__("Atualizar"), () => dashboard.load(), "refresh");
	dashboard.load();
};

class BruceProfessorDashboard {
	constructor(page) {
		this.page = page;
		this.container = $('<div class="bruce-professor-dashboard__content"></div>').appendTo(page.main);
		this.inject_styles();
	}

	load() {
		this.render_loading();

		frappe.call({
			method: "bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.get_next_live_class",
			callback: (response) => {
				const liveClass = response.message;

				if (!liveClass) {
					this.render_empty();
					return;
				}

				this.render_live_class(liveClass);
			},
		});
	}

	render_loading() {
		this.container.html(`
			<div class="bruce-professor-dashboard__panel">
				<div class="text-muted">${__("Carregando próxima aula...")}</div>
			</div>
		`);
	}

	render_empty() {
		this.container.html(`
			<div class="bruce-professor-dashboard__panel">
				<h3>${__("Nenhuma aula ao vivo encontrada.")}</h3>
				<p class="text-muted">${__("Quando houver uma aula agendada ou ao vivo, ela aparecerá aqui.")}</p>
			</div>
		`);
	}

	render_live_class(liveClass) {
		const meetingUrl = this.clean(liveClass.meeting_url);
		const canStart = liveClass.status === "Agendada";
		const startButton = canStart
			? `<button class="btn btn-primary bruce-professor-dashboard__start">${__("Iniciar aula")}</button>`
			: "";
		const openButton = meetingUrl
			? `<button class="btn btn-default bruce-professor-dashboard__open">${__("Abrir aula")}</button>`
			: `<button class="btn btn-default" disabled>${__("Abrir aula")}</button>`;
		const copyButton = meetingUrl
			? `<button class="btn btn-default bruce-professor-dashboard__copy">${__("Copiar link")}</button>`
			: "";
		const whatsappButton = `<button class="btn btn-default bruce-professor-dashboard__whatsapp">${__("Pré-visualizar WhatsApp")}</button>`;
		const deskButton = `<button class="btn btn-default bruce-professor-dashboard__desk">${__("Ir para a aula no Desk")}</button>`;
		const meetingLink = meetingUrl
			? `<a href="${frappe.utils.escape_html(meetingUrl)}" target="_blank" rel="noopener">${frappe.utils.escape_html(meetingUrl)}</a>`
			: `<span class="text-muted">${__("Link indisponível")}</span>`;
		const courseDisplay = this.clean(liveClass.course_title) || this.clean(liveClass.course);
		const batchDisplay = this.clean(liveClass.batch_title) || this.clean(liveClass.batch);
		const classStatusLabel = this.clean(liveClass.class_status_label) || this.clean(liveClass.status);
		const whatsappStatusLabel = this.clean(liveClass.whatsapp_status_label) || this.clean(liveClass.whatsapp_status);

		this.container.html(`
			<div class="bruce-professor-dashboard__panel">
				<div class="bruce-professor-dashboard__header">
					<div>
						<div class="text-muted">${__("Próxima aula")}</div>
						<h3>${frappe.utils.escape_html(this.clean(liveClass.title) || __("Sem título"))}</h3>
					</div>
					<div class="bruce-professor-dashboard__status-stack">
						<span class="indicator-pill ${this.get_class_status_indicator(liveClass.status)}">
							${frappe.utils.escape_html(classStatusLabel || __("Sem status"))}
						</span>
						<span class="indicator-pill ${this.get_whatsapp_status_indicator(whatsappStatusLabel)}">
							${frappe.utils.escape_html(whatsappStatusLabel || __("WhatsApp pendente"))}
						</span>
					</div>
				</div>

				<div class="bruce-professor-dashboard__grid">
					${this.render_field(__("Curso"), courseDisplay)}
					${this.render_field(__("Turma"), batchDisplay)}
					${this.render_field(__("Horário"), this.format_datetime(liveClass.starts_at))}
					${this.render_field(__("Status da aula"), classStatusLabel)}
					${this.render_field(__("Status do WhatsApp"), whatsappStatusLabel)}
					${this.render_field(__("Link da aula"), meetingLink, true)}
				</div>

				<div class="bruce-professor-dashboard__actions">
					${openButton}
					${copyButton}
					${whatsappButton}
					${deskButton}
					${startButton}
				</div>

				${this.render_notice_history(liveClass.notice_logs || [])}
			</div>
		`);

		if (meetingUrl) {
			this.container.find(".bruce-professor-dashboard__open").on("click", () => {
				this.record_notice_event(liveClass.name, "Aula aberta", __("Aula aberta"), __("O link da aula foi aberto pelo usuário."), "Sucesso", () => {
					this.load();
				});
				window.open(meetingUrl, "_blank", "noopener");
			});

			this.container.find(".bruce-professor-dashboard__copy").on("click", () => {
				this.copy_meeting_url(liveClass.name, meetingUrl);
			});
		}

		this.container.find(".bruce-professor-dashboard__whatsapp").on("click", () => {
			this.preview_whatsapp_link(liveClass.name);
		});

		this.container.find(".bruce-professor-dashboard__desk").on("click", () => {
			frappe.set_route("Form", "Bruce Live Class", liveClass.name);
		});

		if (canStart) {
			this.container.find(".bruce-professor-dashboard__start").on("click", () => {
				this.start_live_class(liveClass.name);
			});
		}
	}

	render_field(label, value, isHtml = false) {
		const displayValue = isHtml
			? value
			: frappe.utils.escape_html(this.clean(value) || __("Não informado"));

		return `
			<div class="bruce-professor-dashboard__field">
				<div class="bruce-professor-dashboard__label">${frappe.utils.escape_html(label)}</div>
				<div class="bruce-professor-dashboard__value">${displayValue}</div>
			</div>
		`;
	}

	start_live_class(name) {
		frappe.call({
			method: "bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.start_live_class",
			args: { name },
			freeze: true,
			freeze_message: __("Iniciando aula..."),
			callback: (response) => {
				const result = response.message || {};

				if (result.message) {
					frappe.show_alert({
						message: result.message,
						indicator: "green",
					});
				}

				if (result.meeting_url) {
					window.open(result.meeting_url, "_blank", "noopener");
				}

				this.load();
			},
		});
	}

	preview_whatsapp_link(name) {
		frappe.call({
			method: "bruce_lms_custom.services.whatsapp.preview_live_class_link",
			args: { live_class: name },
			freeze: true,
			freeze_message: __("Montando pré-visualização..."),
			callback: (response) => {
				this.show_whatsapp_preview_dialog(response.message || {});
				this.load();
			},
		});
	}

	show_whatsapp_preview_dialog(result) {
		const recipients = result.recipients || [];
		const recipientRows = recipients.length
			? recipients.map((recipient) => `
				<tr>
					<td>${this.escape_html(recipient.recipient_name || __("Destinatário não informado"))}</td>
					<td>${this.escape_html(recipient.phone || __("Não informado"))}</td>
				</tr>
			`).join("")
			: `<tr><td colspan="2">${this.escape_html(__("Nenhum destinatário encontrado para esta aula."))}</td></tr>`;
		const warning = result.integration_warning
			? `<div class="alert alert-warning" style="margin-bottom: 12px;">${this.escape_html(result.integration_warning)}</div>`
			: "";
		const message = this.escape_html(result.message || "");

		const dialog = new frappe.ui.Dialog({
			title: __("Pré-visualizar WhatsApp"),
			size: "large",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "preview",
					options: `
						${warning}
						<p><strong>${this.escape_html(__("Quantidade de destinatários"))}:</strong> ${Number(result.recipient_count || 0)}</p>
						<div style="max-height: 220px; overflow: auto; margin-bottom: 16px;">
							<table class="table table-bordered">
								<thead>
									<tr>
										<th>${this.escape_html(__("Nome"))}</th>
										<th>${this.escape_html(__("Telefone"))}</th>
									</tr>
								</thead>
								<tbody>${recipientRows}</tbody>
							</table>
						</div>
						<p><strong>${this.escape_html(__("Texto final da mensagem"))}</strong></p>
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

	copy_meeting_url(liveClass, meetingUrl) {
		if (navigator.clipboard && window.isSecureContext) {
			navigator.clipboard.writeText(meetingUrl).then(() => {
				this.show_copy_success();
				this.record_notice_event(liveClass, "Link copiado", __("Link da aula copiado"), __("O link da aula foi copiado pelo usuário."), "Sucesso", () => {
					this.load();
				});
			}).catch(() => {
				this.copy_meeting_url_fallback(liveClass, meetingUrl);
			});
			return;
		}

		this.copy_meeting_url_fallback(liveClass, meetingUrl);
	}

	copy_meeting_url_fallback(liveClass, meetingUrl) {
		const textarea = document.createElement("textarea");
		textarea.value = meetingUrl;
		textarea.setAttribute("readonly", "");
		textarea.style.position = "fixed";
		textarea.style.opacity = "0";
		document.body.appendChild(textarea);
		textarea.select();

		try {
			if (document.execCommand("copy")) {
				this.show_copy_success();
				this.record_notice_event(liveClass, "Link copiado", __("Link da aula copiado"), __("O link da aula foi copiado pelo usuário."), "Sucesso", () => {
					this.load();
				});
			} else {
				this.show_manual_copy_dialog(meetingUrl);
			}
		} catch (error) {
			this.show_manual_copy_dialog(meetingUrl);
		} finally {
			document.body.removeChild(textarea);
		}
	}

	show_copy_success() {
		frappe.show_alert({
			message: __("Link da aula copiado."),
			indicator: "green",
		});
	}

	record_notice_event(liveClass, eventType, title, message, status, callback) {
		frappe.call({
			method: "bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.record_live_class_notice_event",
			args: {
				live_class: liveClass,
				event_type: eventType,
				title,
				message,
				status,
			},
			callback: () => {
				if (callback) {
					callback();
				}
			},
		});
	}

	render_notice_history(logs) {
		const rows = logs.length
			? logs.map((log) => `
				<tr>
					<td>${this.escape_html(this.format_datetime(log.created_at))}</td>
					<td>${this.escape_html(log.title || log.event_type || "")}</td>
					<td>${this.escape_html(log.status || "")}</td>
				</tr>
			`).join("")
			: `<tr><td colspan="3" class="text-muted">${this.escape_html(__("Nenhum aviso ou ação registrado para esta aula."))}</td></tr>`;

		return `
			<div class="bruce-professor-dashboard__history">
				<h4>${this.escape_html(__("Histórico recente"))}</h4>
				<table class="table table-bordered">
					<thead>
						<tr>
							<th>${this.escape_html(__("Data"))}</th>
							<th>${this.escape_html(__("Ação"))}</th>
							<th>${this.escape_html(__("Status"))}</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`;
	}

	show_manual_copy_dialog(meetingUrl) {
		frappe.msgprint({
			title: __("Copiar link da aula"),
			message: __("Não foi possível copiar automaticamente. Copie o link abaixo:") + `<br><br><code>${frappe.utils.escape_html(meetingUrl)}</code>`,
			indicator: "orange",
		});
	}

	format_datetime(value) {
		if (!value) {
			return "";
		}

		return frappe.datetime.str_to_user(value);
	}

	clean(value) {
		return String(value || "").trim();
	}

	get_class_status_indicator(status) {
		if (status === "Ao vivo") {
			return "green";
		}

		if (status === "Agendada") {
			return "blue";
		}

		return "gray";
	}

	get_whatsapp_status_indicator(status) {
		if (status === "WhatsApp enviado") {
			return "green";
		}

		if (status === "WhatsApp falhou") {
			return "red";
		}

		if (status === "Integração desativada") {
			return "gray";
		}

		return "orange";
	}

	escape_html(value) {
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

	inject_styles() {
		if ($("#bruce-professor-dashboard-styles").length) {
			return;
		}

		$(`<style id="bruce-professor-dashboard-styles">
			.bruce-professor-dashboard__content {
				max-width: 920px;
			}

			.bruce-professor-dashboard__panel {
				background: var(--card-bg);
				border: 1px solid var(--border-color);
				border-radius: 8px;
				padding: 24px;
			}

			.bruce-professor-dashboard__header {
				display: flex;
				align-items: flex-start;
				justify-content: space-between;
				gap: 16px;
				margin-bottom: 24px;
			}

			.bruce-professor-dashboard__header h3 {
				margin: 4px 0 0;
			}

			.bruce-professor-dashboard__status-stack {
				display: flex;
				flex-wrap: wrap;
				justify-content: flex-end;
				gap: 8px;
			}

			.bruce-professor-dashboard__grid {
				display: grid;
				grid-template-columns: repeat(2, minmax(0, 1fr));
				gap: 16px;
			}

			.bruce-professor-dashboard__field {
				min-width: 0;
			}

			.bruce-professor-dashboard__label {
				color: var(--text-muted);
				font-size: 12px;
				margin-bottom: 4px;
			}

			.bruce-professor-dashboard__value {
				overflow-wrap: anywhere;
			}

			.bruce-professor-dashboard__actions {
				display: flex;
				flex-wrap: wrap;
				gap: 8px;
				margin-top: 24px;
			}

			.bruce-professor-dashboard__history {
				margin-top: 24px;
			}

			.bruce-professor-dashboard__history h4 {
				margin: 0 0 12px;
			}

			@media (max-width: 640px) {
				.bruce-professor-dashboard__panel {
					padding: 16px;
				}

				.bruce-professor-dashboard__header {
					display: block;
				}

				.bruce-professor-dashboard__header .indicator-pill {
					margin-top: 12px;
				}

				.bruce-professor-dashboard__status-stack {
					justify-content: flex-start;
				}

				.bruce-professor-dashboard__grid {
					grid-template-columns: 1fr;
				}
			}
		</style>`).appendTo("head");
	}
}
