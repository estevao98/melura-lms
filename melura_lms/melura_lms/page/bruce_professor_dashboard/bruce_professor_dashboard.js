["bruce-professor-dashboard", "melura-professor-dashboard"].forEach((pageName) => {
	frappe.pages[pageName] = frappe.pages[pageName] || {};

	frappe.pages[pageName].on_page_load = function (wrapper) {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Painel do professor"),
			single_column: true,
		});

		page.main.addClass("bruce-professor-dashboard");
		const dashboard = new BruceProfessorDashboard(page);

		page.set_primary_action(__("Atualizar"), () => dashboard.load(), "refresh");
		dashboard.load();
	};
});

class BruceProfessorDashboard {
	constructor(page) {
		this.page = page;
		this.container = $('<div class="bruce-professor-dashboard__content"></div>').appendTo(page.main);
		this.inject_styles();
	}

	load() {
		this.render_loading();

		frappe.call({
			method: "melura_lms.melura_lms.page.bruce_professor_dashboard.bruce_professor_dashboard.get_dashboard_data",
			callback: (response) => {
				const dashboardData = response.message || {};
				const liveClass = dashboardData.next_live_class;
				const weekClasses = dashboardData.week_classes || [];
				const classProgress = dashboardData.class_progress || {};

				this.render_dashboard(liveClass, weekClasses, classProgress);
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

	render_dashboard(liveClass, weekClasses, classProgress) {
		this.container.html(`
			${liveClass ? this.render_next_live_class(liveClass) : this.render_empty_next_live_class()}
			${this.render_class_progress(classProgress)}
			${this.render_week_live_classes(weekClasses)}
		`);

		if (liveClass) {
			this.bind_next_live_class_actions(liveClass);
		}
		this.bind_week_live_class_actions(weekClasses);
	}

	render_empty_next_live_class() {
		return `
			<div class="bruce-professor-dashboard__panel">
				<div class="text-muted">${__("Próxima aula")}</div>
				<h3>${__("Nenhuma aula ao vivo encontrada.")}</h3>
				<p class="text-muted">${__("Quando houver uma aula agendada ou ao vivo, ela aparecerá aqui.")}</p>
			</div>
		`;
	}

	render_next_live_class(liveClass) {
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

		return `
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
		`;
	}

	bind_next_live_class_actions(liveClass) {
		const meetingUrl = this.clean(liveClass.meeting_url);
		const canStart = liveClass.status === "Agendada";
		if (meetingUrl) {
			this.container.find(".bruce-professor-dashboard__open").on("click", () => {
				this.record_notice_event(liveClass.name, "Aula aberta", __("Aula aberta"), __("A aula foi aberta pelo usuário no LMS."), "Sucesso", () => {
					this.load();
				});
				this.open_live_room(liveClass.name);
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

	render_class_progress(classProgress) {
		const students = Array.isArray(classProgress.students) ? classProgress.students : [];
		const rows = students.length
			? students.map((student) => this.render_class_progress_row(student)).join("")
			: `<tr><td colspan="7" class="text-muted">${this.escape_html(__("Nenhum progresso disponível para esta turma."))}</td></tr>`;

		return `
			<div class="bruce-professor-dashboard__panel">
				<div class="bruce-professor-dashboard__section-header">
					<h4>${this.escape_html(__("Progresso da turma"))}</h4>
					<div class="text-muted">${this.escape_html(__("Resumo inicial das listas de exercícios"))}</div>
				</div>
				<div class="bruce-professor-dashboard__table-wrap">
					<table class="table table-bordered bruce-professor-dashboard__progress-table">
						<thead>
							<tr>
								<th>${this.escape_html(__("Aluno"))}</th>
								<th>${this.escape_html(__("Status"))}</th>
								<th>${this.escape_html(__("Listas"))}</th>
								<th>${this.escape_html(__("Respondidas"))}</th>
								<th>${this.escape_html(__("Acertos"))}</th>
								<th>${this.escape_html(__("Aproveitamento"))}</th>
								<th>${this.escape_html(__("Última atividade"))}</th>
							</tr>
						</thead>
						<tbody>${rows}</tbody>
					</table>
				</div>
			</div>
		`;
	}

	render_class_progress_row(student) {
		const status = this.clean(student.access_status) || __("Pendente");
		return `
			<tr>
				<td>
					<div class="bruce-professor-dashboard__week-title">${this.escape_html(this.clean(student.student_name) || this.clean(student.student) || __("Aluno"))}</div>
					<div class="text-muted">${this.escape_html(this.clean(student.student) || "")}</div>
				</td>
				<td>
					<span class="indicator-pill ${this.get_access_status_indicator(status)}">${this.escape_html(status)}</span>
				</td>
				<td>${this.escape_html(String(student.total_available_lists || 0))}</td>
				<td>${this.escape_html(String(student.total_answered_questions || 0))}</td>
				<td>${this.escape_html(String(student.total_correct || 0))}</td>
				<td>${this.escape_html(`${this.format_percentage(student.accuracy_percentage)}%`)}</td>
				<td>${this.escape_html(this.format_datetime(student.last_activity) || __("Sem atividade"))}</td>
			</tr>
		`;
	}

	render_week_live_classes(liveClasses) {
		const rows = liveClasses.length
			? liveClasses.map((liveClass) => this.render_week_live_class_row(liveClass)).join("")
			: `<tr><td colspan="7" class="text-muted">${this.escape_html(__("Nenhuma aula agendada para os próximos 7 dias."))}</td></tr>`;

		return `
			<div class="bruce-professor-dashboard__panel bruce-professor-dashboard__week">
				<div class="bruce-professor-dashboard__section-header">
					<h4>${this.escape_html(__("Aulas da semana"))}</h4>
					<div class="text-muted">${this.escape_html(__("Próximos 7 dias"))}</div>
				</div>
				<div class="bruce-professor-dashboard__table-wrap">
					<table class="table table-bordered bruce-professor-dashboard__week-table">
						<thead>
							<tr>
								<th>${this.escape_html(__("Aula"))}</th>
								<th>${this.escape_html(__("Curso"))}</th>
								<th>${this.escape_html(__("Turma"))}</th>
								<th>${this.escape_html(__("Data e horário"))}</th>
								<th>${this.escape_html(__("Status"))}</th>
								<th>${this.escape_html(__("WhatsApp"))}</th>
								<th>${this.escape_html(__("Ações"))}</th>
							</tr>
						</thead>
						<tbody>${rows}</tbody>
					</table>
				</div>
			</div>
		`;
	}

	render_week_live_class_row(liveClass) {
		const meetingUrl = this.clean(liveClass.meeting_url);
		const courseDisplay = this.clean(liveClass.course_title) || this.clean(liveClass.course);
		const batchDisplay = this.clean(liveClass.batch_title) || this.clean(liveClass.batch);
		const classStatusLabel = this.clean(liveClass.class_status_label) || this.clean(liveClass.status);
		const whatsappStatusLabel = this.clean(liveClass.whatsapp_status_label) || this.clean(liveClass.whatsapp_status);
		const openButton = meetingUrl
			? `<button class="btn btn-xs btn-default bruce-professor-dashboard__week-open" data-name="${this.escape_attr(liveClass.name)}">${this.escape_html(__("Abrir aula"))}</button>`
			: `<button class="btn btn-xs btn-default" disabled>${this.escape_html(__("Abrir aula"))}</button>`;
		const copyButton = meetingUrl
			? `<button class="btn btn-xs btn-default bruce-professor-dashboard__week-copy" data-name="${this.escape_attr(liveClass.name)}">${this.escape_html(__("Copiar link"))}</button>`
			: `<button class="btn btn-xs btn-default" disabled>${this.escape_html(__("Copiar link"))}</button>`;

		return `
			<tr>
				<td>
					<div class="bruce-professor-dashboard__week-title">${this.escape_html(this.clean(liveClass.title) || __("Sem título"))}</div>
				</td>
				<td>${this.escape_html(courseDisplay || __("Não informado"))}</td>
				<td>${this.escape_html(batchDisplay || __("Não informado"))}</td>
				<td>${this.escape_html(this.format_datetime(liveClass.starts_at) || __("Não informado"))}</td>
				<td>
					<span class="indicator-pill ${this.get_class_status_indicator(liveClass.status)}">
						${this.escape_html(classStatusLabel || __("Sem status"))}
					</span>
				</td>
				<td>
					<span class="indicator-pill ${this.get_whatsapp_status_indicator(whatsappStatusLabel)}">
						${this.escape_html(whatsappStatusLabel || __("WhatsApp pendente"))}
					</span>
				</td>
				<td>
					<div class="bruce-professor-dashboard__row-actions">
						${openButton}
						${copyButton}
						<button class="btn btn-xs btn-default bruce-professor-dashboard__week-details" data-name="${this.escape_attr(liveClass.name)}">${this.escape_html(__("Ver detalhes"))}</button>
					</div>
				</td>
			</tr>
		`;
	}

	bind_week_live_class_actions(liveClasses) {
		const liveClassesByName = {};
		(liveClasses || []).forEach((liveClass) => {
			liveClassesByName[liveClass.name] = liveClass;
		});

		this.container.find(".bruce-professor-dashboard__week-open").on("click", (event) => {
			const liveClass = liveClassesByName[$(event.currentTarget).data("name")];
			const meetingUrl = this.clean(liveClass && liveClass.meeting_url);

			if (!liveClass || !meetingUrl) {
				return;
			}

			this.record_notice_event(liveClass.name, "Aula aberta", __("Aula aberta"), __("A aula foi aberta pelo usuário no LMS."), "Sucesso", () => {
				this.load();
			});
			this.open_live_room(liveClass.name);
		});

		this.container.find(".bruce-professor-dashboard__week-copy").on("click", (event) => {
			const liveClass = liveClassesByName[$(event.currentTarget).data("name")];
			const meetingUrl = this.clean(liveClass && liveClass.meeting_url);

			if (liveClass && meetingUrl) {
				this.copy_meeting_url(liveClass.name, meetingUrl);
			}
		});

		this.container.find(".bruce-professor-dashboard__week-details").on("click", (event) => {
			frappe.set_route("Form", "Bruce Live Class", $(event.currentTarget).data("name"));
		});
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
			method: "melura_lms.melura_lms.doctype.bruce_live_class.bruce_live_class.start_live_class",
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

				if (result.name) {
					this.open_live_room(result.name);
				}

				this.load();
			},
		});
	}

	open_live_room(liveClass) {
		frappe.set_route("melura-live-room", liveClass);
	}

	preview_whatsapp_link(name) {
		frappe.call({
			method: "melura_lms.services.whatsapp.preview_live_class_link",
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
			method: "melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.record_live_class_notice_event",
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

	format_percentage(value) {
		const number = Number(value || 0);
		return Number.isInteger(number) ? String(number) : number.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
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

	get_access_status_indicator(status) {
		if (status === "Ativo") {
			return "green";
		}

		if (status === "Pendente") {
			return "orange";
		}

		if (status === "Bloqueado" || status === "Expirado") {
			return "red";
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

	escape_attr(value) {
		return this.escape_html(value);
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

			.bruce-professor-dashboard__panel + .bruce-professor-dashboard__panel {
				margin-top: 16px;
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

			.bruce-professor-dashboard__section-header {
				display: flex;
				align-items: baseline;
				justify-content: space-between;
				gap: 12px;
				margin-bottom: 12px;
			}

			.bruce-professor-dashboard__section-header h4 {
				margin: 0;
			}

			.bruce-professor-dashboard__table-wrap {
				overflow-x: auto;
			}

			.bruce-professor-dashboard__week-table,
			.bruce-professor-dashboard__progress-table {
				margin-bottom: 0;
				min-width: 860px;
			}

			.bruce-professor-dashboard__week-table th,
			.bruce-professor-dashboard__week-table td,
			.bruce-professor-dashboard__progress-table th,
			.bruce-professor-dashboard__progress-table td {
				vertical-align: middle;
			}

			.bruce-professor-dashboard__progress-table .indicator-pill {
				display: inline-flex;
				align-items: center;
				white-space: nowrap;
			}

			.bruce-professor-dashboard__week-table th:nth-child(5),
			.bruce-professor-dashboard__week-table td:nth-child(5) {
				min-width: 132px;
			}

			.bruce-professor-dashboard__week-table th:nth-child(6),
			.bruce-professor-dashboard__week-table td:nth-child(6) {
				min-width: 180px;
			}

			.bruce-professor-dashboard__week-table .indicator-pill {
				display: inline-flex;
				align-items: center;
				white-space: nowrap;
			}

			.bruce-professor-dashboard__week-title {
				font-weight: 600;
				overflow-wrap: anywhere;
			}

			.bruce-professor-dashboard__row-actions {
				display: flex;
				flex-wrap: wrap;
				gap: 6px;
				min-width: 210px;
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

				.bruce-professor-dashboard__section-header {
					display: block;
				}
			}
		</style>`).appendTo("head");
	}
}
