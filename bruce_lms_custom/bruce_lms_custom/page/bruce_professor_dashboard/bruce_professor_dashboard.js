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
		const whatsappButton = meetingUrl
			? `<button class="btn btn-default bruce-professor-dashboard__whatsapp">${__("Enviar link por WhatsApp")}</button>`
			: "";
		const meetingLink = meetingUrl
			? `<a href="${frappe.utils.escape_html(meetingUrl)}" target="_blank" rel="noopener">${frappe.utils.escape_html(meetingUrl)}</a>`
			: `<span class="text-muted">${__("Link indisponível")}</span>`;
		const courseDisplay = this.clean(liveClass.course_title) || this.clean(liveClass.course);
		const batchDisplay = this.clean(liveClass.batch_title) || this.clean(liveClass.batch);

		this.container.html(`
			<div class="bruce-professor-dashboard__panel">
				<div class="bruce-professor-dashboard__header">
					<div>
						<div class="text-muted">${__("Próxima aula")}</div>
						<h3>${frappe.utils.escape_html(this.clean(liveClass.title) || __("Sem título"))}</h3>
					</div>
					<span class="indicator-pill ${this.get_status_indicator(liveClass.status)}">
						${frappe.utils.escape_html(this.clean(liveClass.status) || __("Sem status"))}
					</span>
				</div>

				<div class="bruce-professor-dashboard__grid">
					${this.render_field(__("Curso"), courseDisplay)}
					${this.render_field(__("Turma"), batchDisplay)}
					${this.render_field(__("Início"), this.format_datetime(liveClass.starts_at))}
					${this.render_field(__("Status do WhatsApp"), liveClass.whatsapp_status)}
					${this.render_field(__("Link da aula"), meetingLink, true)}
				</div>

				<div class="bruce-professor-dashboard__actions">
					${openButton}
					${copyButton}
					${whatsappButton}
					${startButton}
				</div>
			</div>
		`);

		if (meetingUrl) {
			this.container.find(".bruce-professor-dashboard__open").on("click", () => {
				window.open(meetingUrl, "_blank", "noopener");
			});

			this.container.find(".bruce-professor-dashboard__copy").on("click", () => {
				this.copy_meeting_url(meetingUrl);
			});

			this.container.find(".bruce-professor-dashboard__whatsapp").on("click", () => {
				this.send_whatsapp_link(liveClass.name);
			});
		}

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

	send_whatsapp_link(name) {
		frappe.call({
			method: "bruce_lms_custom.services.whatsapp.send_live_class_link",
			args: { live_class: name },
			freeze: true,
			freeze_message: __("Enviando link por WhatsApp..."),
			callback: (response) => {
				const result = response.message || {};

				frappe.show_alert({
					message: result.message || __("Solicitação de envio registrada."),
					indicator: result.status === "sent" ? "green" : "orange",
				});

				this.load();
			},
		});
	}

	copy_meeting_url(meetingUrl) {
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
				this.show_manual_copy_dialog(meetingUrl);
			});
			return;
		}

		this.show_manual_copy_dialog(meetingUrl);
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

	get_status_indicator(status) {
		if (status === "Ao vivo") {
			return "green";
		}

		if (status === "Agendada") {
			return "blue";
		}

		return "gray";
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

				.bruce-professor-dashboard__grid {
					grid-template-columns: 1fr;
				}
			}
		</style>`).appendTo("head");
	}
}
