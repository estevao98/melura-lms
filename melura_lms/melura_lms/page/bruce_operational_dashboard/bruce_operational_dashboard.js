["bruce-operational-dashboard", "melura-operational-dashboard"].forEach((pageName) => {
	frappe.pages[pageName] = frappe.pages[pageName] || {};

	frappe.pages[pageName].on_page_load = function (wrapper) {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Painel operacional"),
			single_column: true,
		});

		page.main.addClass("bruce-operational-dashboard");
		const dashboard = new BruceOperationalDashboard(page);

		page.set_primary_action(__("Atualizar"), () => dashboard.load(), "refresh");
		dashboard.load();
	};
});

class BruceOperationalDashboard {
	constructor(page) {
		this.page = page;
		this.container = $('<div class="bruce-operational-dashboard__content"></div>').appendTo(page.main);
		this.inject_styles();
	}

	load() {
		this.render_loading();

		frappe.call({
			method: "melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.get_dashboard_data",
			callback: (response) => {
				this.render_dashboard(response.message || {});
			},
		});
	}

	render_loading() {
		this.container.html(`
			<div class="bruce-operational-dashboard__panel">
				<div class="text-muted">${this.escape_html(__("Carregando dados operacionais..."))}</div>
			</div>
		`);
	}

	render_dashboard(data) {
		const overview = data.overview || {};
		const classes = data.classes || {};
		const content = data.content || {};
		const exercisesProgress = data.exercises_progress || {};
		const alerts = data.alerts || [];

		this.container.html(`
			${this.render_overview(overview)}
			${this.render_classes(classes)}
			${this.render_content(content)}
			${this.render_exercises_progress(exercisesProgress)}
			${this.render_alerts(alerts, classes, exercisesProgress)}
		`);
		this.bind_actions();
	}

	render_overview(overview) {
		const cards = [
			[__("Alunos com acesso"), overview.total_students_with_access],
			[__("Alunos ativos"), overview.active_students],
			[__("Alunos pendentes"), overview.pending_students],
			[__("Alunos bloqueados"), overview.blocked_students],
			[__("Alunos expirados"), overview.expired_students],
			[__("Aulas da semana"), overview.week_live_classes],
			[__("Respostas registradas"), overview.registered_answers],
			[__("Aproveitamento médio"), `${this.format_percentage(overview.average_accuracy)}%`],
		];

		return `
			<div class="bruce-operational-dashboard__panel">
				<div class="bruce-operational-dashboard__section-header">
					<h4>${this.escape_html(__("Visão geral"))}</h4>
					<div class="text-muted">${this.escape_html(__("Resumo acadêmico e operacional"))}</div>
				</div>
				<div class="bruce-operational-dashboard__cards">
					${cards.map(([label, value]) => this.render_metric_card(label, value)).join("")}
				</div>
			</div>
		`;
	}

	render_classes(classes) {
		const withoutRoom = classes.upcoming_classes_without_room || [];
		const rows = withoutRoom.length
			? withoutRoom.map((liveClass) => this.render_class_row(liveClass)).join("")
			: `<tr><td colspan="5" class="text-muted">${this.escape_html(__("Nenhuma aula da semana sem link ou sala."))}</td></tr>`;

		return `
			<div class="bruce-operational-dashboard__panel">
				<div class="bruce-operational-dashboard__section-header">
					<h4>${this.escape_html(__("Aulas"))}</h4>
					<div class="text-muted">${this.escape_html(__("Próximos 7 dias"))}</div>
				</div>
				<div class="bruce-operational-dashboard__cards bruce-operational-dashboard__cards--compact">
					${this.render_metric_card(__("Aulas ao vivo da semana"), classes.week_live_classes)}
					${this.render_metric_card(__("Sem link ou sala"), withoutRoom.length)}
				</div>
				<div class="bruce-operational-dashboard__table-wrap">
					<table class="table table-bordered">
						<thead>
							<tr>
								<th>${this.escape_html(__("Aula"))}</th>
								<th>${this.escape_html(__("Curso"))}</th>
								<th>${this.escape_html(__("Turma"))}</th>
								<th>${this.escape_html(__("Início"))}</th>
								<th>${this.escape_html(__("Ações"))}</th>
							</tr>
						</thead>
						<tbody>${rows}</tbody>
					</table>
				</div>
			</div>
		`;
	}

	render_content(content) {
		return `
			<div class="bruce-operational-dashboard__panel">
				<div class="bruce-operational-dashboard__section-header">
					<h4>${this.escape_html(__("Conteúdo"))}</h4>
					<div class="text-muted">${this.escape_html(__("Itens publicados"))}</div>
				</div>
				<div class="bruce-operational-dashboard__cards bruce-operational-dashboard__cards--compact">
					${this.render_metric_card(__("Materiais publicados"), content.published_materials)}
					${this.render_metric_card(__("Questões ENEM publicadas"), content.published_questions)}
					${this.render_metric_card(__("Listas publicadas"), content.published_exercise_lists)}
				</div>
			</div>
		`;
	}

	render_exercises_progress(exercisesProgress) {
		const inactiveStudents = exercisesProgress.inactive_students || [];
		const rows = inactiveStudents.length
			? inactiveStudents.map((student) => this.render_inactive_student_row(student)).join("")
			: `<tr><td colspan="3" class="text-muted">${this.escape_html(__("Nenhum aluno ativo sem atividade recente identificado."))}</td></tr>`;

		return `
			<div class="bruce-operational-dashboard__panel">
				<div class="bruce-operational-dashboard__section-header">
					<h4>${this.escape_html(__("Exercícios e progresso"))}</h4>
					<div class="text-muted">${this.escape_html(__("Resumo simples por respostas registradas"))}</div>
				</div>
				<div class="bruce-operational-dashboard__cards bruce-operational-dashboard__cards--compact">
					${this.render_metric_card(__("Respostas registradas"), exercisesProgress.registered_answers)}
					${this.render_metric_card(__("Acertos"), exercisesProgress.correct_answers)}
					${this.render_metric_card(__("Aproveitamento médio"), `${this.format_percentage(exercisesProgress.average_accuracy)}%`)}
					${this.render_metric_card(__("Sem atividade recente"), inactiveStudents.length)}
				</div>
				<div class="bruce-operational-dashboard__table-wrap">
					<table class="table table-bordered">
						<thead>
							<tr>
								<th>${this.escape_html(__("Aluno"))}</th>
								<th>${this.escape_html(__("Última atividade"))}</th>
								<th>${this.escape_html(__("Ações"))}</th>
							</tr>
						</thead>
						<tbody>${rows}</tbody>
					</table>
				</div>
			</div>
		`;
	}

	render_alerts(alerts) {
		return `
			<div class="bruce-operational-dashboard__panel">
				<div class="bruce-operational-dashboard__section-header">
					<h4>${this.escape_html(__("Alertas operacionais"))}</h4>
					<div class="text-muted">${this.escape_html(__("Pendências simples para acompanhamento"))}</div>
				</div>
				<div class="bruce-operational-dashboard__alerts">
					${alerts.map((alert) => this.render_alert(alert)).join("")}
				</div>
			</div>
		`;
	}

	render_metric_card(label, value) {
		return `
			<div class="bruce-operational-dashboard__metric">
				<div class="bruce-operational-dashboard__metric-label">${this.escape_html(label)}</div>
				<div class="bruce-operational-dashboard__metric-value">${this.escape_html(this.clean(value) || "0")}</div>
			</div>
		`;
	}

	render_class_row(liveClass) {
		const courseDisplay = this.clean(liveClass.course_title) || this.clean(liveClass.course);
		const batchDisplay = this.clean(liveClass.batch_title) || this.clean(liveClass.batch);

		return `
			<tr>
				<td>${this.escape_html(this.clean(liveClass.title) || __("Sem título"))}</td>
				<td>${this.escape_html(courseDisplay || __("Não informado"))}</td>
				<td>${this.escape_html(batchDisplay || __("Não informado"))}</td>
				<td>${this.escape_html(this.format_datetime(liveClass.starts_at) || __("Não informado"))}</td>
				<td>
					<button class="btn btn-xs btn-default bruce-operational-dashboard__open-class" data-name="${this.escape_attr(liveClass.name)}">
						${this.escape_html(__("Ver detalhes"))}
					</button>
				</td>
			</tr>
		`;
	}

	render_inactive_student_row(student) {
		return `
			<tr>
				<td>
					<div class="bruce-operational-dashboard__row-title">${this.escape_html(this.clean(student.student_name) || this.clean(student.student))}</div>
					<div class="text-muted">${this.escape_html(this.clean(student.student))}</div>
				</td>
				<td>${this.escape_html(this.format_datetime(student.last_activity) || __("Sem resposta registrada"))}</td>
				<td>
					<button class="btn btn-xs btn-default bruce-operational-dashboard__open-student" data-name="${this.escape_attr(student.student)}">
						${this.escape_html(__("Abrir usuário"))}
					</button>
				</td>
			</tr>
		`;
	}

	render_alert(alert) {
		return `
			<div class="bruce-operational-dashboard__alert bruce-operational-dashboard__alert--${this.escape_attr(alert.severity || "warning")}">
				<div class="bruce-operational-dashboard__row-title">${this.escape_html(alert.title || __("Alerta"))}</div>
				<div class="text-muted">${this.escape_html(alert.message || "")}</div>
			</div>
		`;
	}

	bind_actions() {
		this.container.find(".bruce-operational-dashboard__open-class").on("click", (event) => {
			frappe.set_route("Form", "Bruce Live Class", $(event.currentTarget).data("name"));
		});
		this.container.find(".bruce-operational-dashboard__open-student").on("click", (event) => {
			frappe.set_route("Form", "User", $(event.currentTarget).data("name"));
		});
	}

	format_datetime(value) {
		if (!value) {
			return "";
		}

		return frappe.datetime.str_to_user(value);
	}

	format_percentage(value) {
		const numberValue = Number(value || 0);
		return Number.isInteger(numberValue) ? String(numberValue) : numberValue.toFixed(1);
	}

	clean(value) {
		if (value === null || value === undefined) {
			return "";
		}

		return String(value);
	}

	escape_html(value) {
		return frappe.utils.escape_html(this.clean(value));
	}

	escape_attr(value) {
		return this.escape_html(value).replace(/"/g, "&quot;");
	}

	inject_styles() {
		if ($("#bruce-operational-dashboard-styles").length) {
			return;
		}

		$(`<style id="bruce-operational-dashboard-styles">
			.bruce-operational-dashboard__content {
				display: flex;
				flex-direction: column;
				gap: 16px;
				padding-bottom: 24px;
			}

			.bruce-operational-dashboard__panel {
				background: var(--card-bg);
				border: 1px solid var(--border-color);
				border-radius: 8px;
				padding: 16px;
			}

			.bruce-operational-dashboard__section-header {
				display: flex;
				justify-content: space-between;
				gap: 12px;
				align-items: flex-start;
				margin-bottom: 12px;
			}

			.bruce-operational-dashboard__section-header h4 {
				margin: 0;
				font-size: 16px;
				font-weight: 600;
			}

			.bruce-operational-dashboard__cards {
				display: grid;
				grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
				gap: 12px;
			}

			.bruce-operational-dashboard__cards--compact {
				margin-bottom: 12px;
			}

			.bruce-operational-dashboard__metric {
				border: 1px solid var(--border-color);
				border-radius: 8px;
				padding: 12px;
				min-height: 82px;
				background: var(--bg-light-gray);
			}

			.bruce-operational-dashboard__metric-label {
				color: var(--text-muted);
				font-size: 12px;
				line-height: 1.3;
				min-height: 32px;
			}

			.bruce-operational-dashboard__metric-value {
				font-size: 24px;
				font-weight: 600;
				line-height: 1.2;
				margin-top: 4px;
			}

			.bruce-operational-dashboard__table-wrap {
				overflow-x: auto;
			}

			.bruce-operational-dashboard__row-title {
				font-weight: 600;
			}

			.bruce-operational-dashboard__alerts {
				display: flex;
				flex-direction: column;
				gap: 8px;
			}

			.bruce-operational-dashboard__alert {
				border: 1px solid var(--border-color);
				border-radius: 8px;
				padding: 12px;
			}

			.bruce-operational-dashboard__alert--warning {
				border-left: 4px solid var(--yellow-500);
			}

			.bruce-operational-dashboard__alert--success {
				border-left: 4px solid var(--green-500);
			}

			@media (max-width: 768px) {
				.bruce-operational-dashboard__section-header {
					display: block;
				}
			}
		</style>`).appendTo("head");
	}
}
