frappe.pages["minha-aula"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Minha Aula"),
		single_column: true,
	});

	page.main.addClass("bruce-student-dashboard");
	const dashboard = new BruceStudentDashboard(page);

	page.set_primary_action(__("Atualizar"), () => dashboard.load(), "refresh");
	dashboard.load();
};

class BruceStudentDashboard {
	constructor(page) {
		this.page = page;
		this.container = $('<div class="bruce-student-dashboard__content"></div>').appendTo(page.main);
		this.inject_styles();
	}

	load() {
		this.render_loading();

		frappe.call({
				method: "zuno_lms.zuno_lms.page.minha_aula.minha_aula.get_student_dashboard_data",
				callback: (response) => {
					const dashboardData = response.message || {};
					this.render_dashboard(dashboardData);
				},
			});
	}

	render_loading() {
		this.container.html(`
			<div class="bruce-student-dashboard__panel">
				<div class="text-muted">${this.escape_html(__("Carregando sua aula e materiais..."))}</div>
			</div>
		`);
	}

	render_dashboard(dashboardData) {
		const liveClass = dashboardData.next_live_class;
		const materials = Array.isArray(dashboardData.recent_materials) ? dashboardData.recent_materials : [];
		const exerciseLists = Array.isArray(dashboardData.exercise_lists) ? dashboardData.exercise_lists : [];
		const studentProgress = dashboardData.student_progress || {};
		this.container.html(`
			${liveClass ? this.render_next_live_class(liveClass) : this.render_empty_state(dashboardData)}
			${this.render_student_progress(studentProgress)}
			${this.render_exercise_lists_section(exerciseLists)}
			${this.render_materials_section(materials)}
		`);

		if (liveClass) {
			this.bind_live_class_actions(liveClass);
		}

		this.bind_material_actions(materials);
		this.bind_exercise_list_actions();
	}

	render_empty_state(dashboardData) {
		const accessStatus = this.clean(dashboardData.access_status);
		const studentFilterNote = this.clean(dashboardData.student_filter_note)
			|| __("Quando houver uma aula ao vivo disponível, ela aparecerá aqui.");
		const title = dashboardData.student_is_active
			? __("Nenhuma aula agendada no momento.")
			: __("Acesso não liberado.");

		return `
			<div class="bruce-student-dashboard__panel">
				<div class="text-muted">${this.escape_html(__("Próxima aula ao vivo"))}</div>
				<h3>${this.escape_html(title)}</h3>
				${accessStatus ? `<p><span class="indicator-pill ${this.get_access_status_indicator(accessStatus)}">${this.escape_html(accessStatus)}</span></p>` : ""}
				<p class="text-muted">${this.escape_html(studentFilterNote)}</p>
			</div>
		`;
	}

	render_next_live_class(liveClass) {
		const meetingUrl = this.clean(liveClass.meeting_url);
		const courseDisplay = this.clean(liveClass.course_title) || this.clean(liveClass.course);
		const batchDisplay = this.clean(liveClass.batch_title) || this.clean(liveClass.batch);
		const classStatusLabel = this.clean(liveClass.class_status_label) || this.clean(liveClass.status);
		const enterButton = meetingUrl
			? `<button class="btn btn-primary bruce-student-dashboard__enter">${this.escape_html(__("Entrar na aula"))}</button>`
			: `<button class="btn btn-primary" disabled>${this.escape_html(__("Entrar na aula"))}</button>`;
		const copyButton = meetingUrl
			? `<button class="btn btn-default bruce-student-dashboard__copy">${this.escape_html(__("Copiar link"))}</button>`
			: `<button class="btn btn-default" disabled>${this.escape_html(__("Copiar link"))}</button>`;

		return `
			<div class="bruce-student-dashboard__panel">
				<div class="bruce-student-dashboard__header">
					<div>
						<div class="text-muted">${this.escape_html(__("Próxima aula ao vivo"))}</div>
						<h3>${this.escape_html(this.clean(liveClass.title) || __("Sem título"))}</h3>
					</div>
					<span class="indicator-pill ${this.get_class_status_indicator(liveClass.status)}">
						${this.escape_html(classStatusLabel || __("Sem status"))}
					</span>
				</div>

				<div class="bruce-student-dashboard__grid">
					${this.render_field(__("Curso"), courseDisplay)}
					${this.render_field(__("Turma"), batchDisplay)}
					${this.render_field(__("Data e horário"), this.format_datetime(liveClass.starts_at))}
					${this.render_field(__("Status da aula"), classStatusLabel)}
				</div>

				<div class="bruce-student-dashboard__actions">
					${enterButton}
					${copyButton}
				</div>
			</div>
		`;
	}

	render_student_progress(progress) {
		const locked = Boolean(progress.locked);
		const accessStatus = this.clean(progress.access_status);

		if (locked) {
			return `
				<div class="bruce-student-dashboard__panel">
					<div class="text-muted">${this.escape_html(__("Meu progresso"))}</div>
					<h3>${this.escape_html(__("Progresso ainda não liberado"))}</h3>
					${accessStatus ? `<p><span class="indicator-pill ${this.get_access_status_indicator(accessStatus)}">${this.escape_html(accessStatus)}</span></p>` : ""}
					<p class="text-muted mb-0">${this.escape_html(__("Seu progresso aparece aqui quando seu acesso pedagógico estiver ativo."))}</p>
				</div>
			`;
		}

		return `
			<div class="bruce-student-dashboard__panel">
				<div class="bruce-student-dashboard__section-title">
					<div>
						<div class="text-muted">${this.escape_html(__("Meu progresso"))}</div>
						<h3>${this.escape_html(__("Desempenho nas listas"))}</h3>
					</div>
					<span class="indicator-pill ${progress.is_recently_active ? "green" : "gray"}">
						${this.escape_html(progress.is_recently_active ? __("Aluno ativo") : __("Sem atividade recente"))}
					</span>
				</div>
				<div class="bruce-student-dashboard__progress-grid">
					${this.render_metric(__("Questões respondidas"), progress.total_answered_questions)}
					${this.render_metric(__("Acertos"), progress.total_correct)}
					${this.render_metric(__("Erros"), progress.total_errors)}
					${this.render_metric(__("Aproveitamento"), `${this.format_percentage(progress.accuracy_percentage)}%`)}
					${this.render_metric(__("Última atividade"), this.format_datetime(progress.last_activity) || __("Sem atividade"))}
				</div>
			</div>
		`;
	}

	render_metric(label, value) {
		return `
			<div class="bruce-student-dashboard__metric">
				<div class="bruce-student-dashboard__label">${this.escape_html(label)}</div>
				<div class="bruce-student-dashboard__metric-value">${this.escape_html(this.clean(value) || "0")}</div>
			</div>
		`;
	}

	render_materials_section(materials) {
		return `
			<div class="bruce-student-dashboard__panel bruce-student-dashboard__materials">
				<div class="bruce-student-dashboard__section-title">
					<div>
						<div class="text-muted">${this.escape_html(__("Materiais"))}</div>
						<h3>${this.escape_html(__("Materiais recentes"))}</h3>
					</div>
				</div>
				${materials.length ? this.render_materials_list(materials) : this.render_empty_materials()}
			</div>
		`;
	}

	render_exercise_lists_section(exerciseLists) {
		return `
			<div class="bruce-student-dashboard__panel bruce-student-dashboard__exercise-lists">
				<div class="bruce-student-dashboard__section-title">
					<div>
						<div class="text-muted">${this.escape_html(__("Listas de exercícios"))}</div>
						<h3>${this.escape_html(__("Listas disponíveis"))}</h3>
					</div>
				</div>
				${exerciseLists.length ? this.render_exercise_lists(exerciseLists) : this.render_empty_exercise_lists()}
			</div>
		`;
	}

	render_exercise_lists(exerciseLists) {
		return `
			<div class="bruce-student-dashboard__exercise-list">
				${exerciseLists.map((exerciseList) => this.render_exercise_list_item(exerciseList)).join("")}
			</div>
		`;
	}

	render_exercise_list_item(exerciseList) {
		const questionCount = Number(exerciseList.question_count || 0);
		const questionLabel = questionCount === 1 ? __("1 questão") : __("{0} questões", [questionCount]);
		const dueDate = this.format_datetime(exerciseList.due_date);

		return `
			<div class="bruce-student-dashboard__exercise-item">
				<div class="bruce-student-dashboard__exercise-main">
					<div class="bruce-student-dashboard__material-title">${this.escape_html(this.clean(exerciseList.title) || __("Sem título"))}</div>
					<div class="bruce-student-dashboard__material-meta">
						${this.escape_html(questionLabel)}
						${dueDate ? ` · ${this.escape_html(__("Prazo: {0}", [dueDate]))}` : ""}
					</div>
				</div>
				<div class="bruce-student-dashboard__material-action">
					<button
						class="btn btn-primary btn-sm bruce-student-dashboard__answer-list"
						data-exercise-list="${this.escape_attribute(exerciseList.name)}"
					>
						${this.escape_html(__("Responder"))}
					</button>
				</div>
			</div>
		`;
	}

	render_empty_exercise_lists() {
		return `<p class="text-muted mb-0">${this.escape_html(__("Nenhuma lista de exercícios disponível no momento."))}</p>`;
	}

	render_materials_list(materials) {
		return `
			<div class="bruce-student-dashboard__material-list">
				${materials.map((material) => this.render_material_item(material)).join("")}
			</div>
		`;
	}

	render_material_item(material) {
		const courseDisplay = this.clean(material.course_title) || this.clean(material.course);
		const batchDisplay = this.clean(material.batch_title) || this.clean(material.batch);
		const liveClassDisplay = this.clean(material.related_live_class_title) || this.clean(material.related_live_class);
		const hasPdf = Boolean(this.clean(material.pdf_file));
		const actionLabel = hasPdf ? __("Baixar PDF") : __("Abrir material");

		return `
			<div class="bruce-student-dashboard__material-item">
				<div class="bruce-student-dashboard__material-main">
					<div class="bruce-student-dashboard__material-title">${this.escape_html(this.clean(material.title) || __("Sem título"))}</div>
					<div class="bruce-student-dashboard__material-meta">
						${this.escape_html(this.clean(material.material_type) || __("Material"))}
					</div>
					<div class="bruce-student-dashboard__material-grid">
						${this.render_field(__("Curso"), courseDisplay)}
						${this.render_field(__("Turma"), batchDisplay)}
						${this.render_field(__("Aula relacionada"), liveClassDisplay)}
					</div>
				</div>
				<div class="bruce-student-dashboard__material-action">
					<button
						class="btn btn-default btn-sm bruce-student-dashboard__open-material"
						data-material-name="${this.escape_attribute(material.name)}"
						data-pdf-file="${this.escape_attribute(material.pdf_file)}"
					>
						${this.escape_html(actionLabel)}
					</button>
				</div>
			</div>
		`;
	}

	render_empty_materials() {
		return `<p class="text-muted mb-0">${this.escape_html(__("Nenhum material disponível no momento."))}</p>`;
	}

	bind_live_class_actions(liveClass) {
		const meetingUrl = this.clean(liveClass.meeting_url);

		if (!meetingUrl) {
			return;
		}

		this.container.find(".bruce-student-dashboard__enter").on("click", () => {
			this.open_live_room(liveClass.name);
		});

		this.container.find(".bruce-student-dashboard__copy").on("click", () => {
			this.copy_meeting_url(meetingUrl);
		});
	}

	open_live_room(liveClass) {
		frappe.set_route("bruce-live-room", liveClass);
	}

	bind_material_actions() {
		this.container.find(".bruce-student-dashboard__open-material").on("click", (event) => {
			const button = $(event.currentTarget);
			const pdfFile = this.clean(button.attr("data-pdf-file"));
			const materialName = this.clean(button.attr("data-material-name"));

			if (pdfFile) {
				window.open(pdfFile, "_blank", "noopener");
				return;
			}

			if (materialName) {
				frappe.set_route("Form", "Bruce Educational Material", materialName);
			}
		});
	}

	bind_exercise_list_actions() {
		this.container.find(".bruce-student-dashboard__answer-list").on("click", (event) => {
			const exerciseList = this.clean($(event.currentTarget).attr("data-exercise-list"));
			if (exerciseList) {
				this.open_exercise_list(exerciseList);
			}
		});
	}

	open_exercise_list(exerciseList) {
		frappe.call({
			method: "zuno_lms.services.student_access.get_exercise_list_for_current_student",
			args: {
				exercise_list: exerciseList,
			},
			callback: (response) => {
				this.show_exercise_dialog(response.message || {});
			},
		});
	}

	show_exercise_dialog(exerciseList) {
		const questions = Array.isArray(exerciseList.questions) ? exerciseList.questions : [];
		const dialog = new frappe.ui.Dialog({
			title: this.clean(exerciseList.title) || __("Lista de exercícios"),
			size: "large",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "exercise_html",
					options: questions.length
						? this.render_exercise_questions(questions)
						: `<p class="text-muted">${this.escape_html(__("Nenhuma questão disponível nesta lista."))}</p>`,
				},
			],
			primary_action_label: __("Salvar respostas"),
			primary_action: () => this.save_exercise_answers(dialog, exerciseList, questions),
		});

		dialog.show();
	}

	render_exercise_questions(questions) {
		return `
			<div class="bruce-exercise-dialog">
				${questions.map((question, index) => this.render_exercise_question(question, index)).join("")}
			</div>
		`;
	}

	render_exercise_question(question, index) {
		const alternatives = Array.isArray(question.alternatives) ? question.alternatives : [];
		return `
			<div class="bruce-exercise-dialog__question" data-question="${this.escape_attribute(question.name)}">
				<div class="bruce-exercise-dialog__title">${this.escape_html(__("Questão {0}", [index + 1]))}</div>
				<div class="bruce-exercise-dialog__statement">${question.statement || ""}</div>
				<div class="bruce-exercise-dialog__alternatives">
					${alternatives.map((alternative) => this.render_exercise_alternative(question, alternative)).join("")}
				</div>
				<div class="bruce-exercise-dialog__result text-muted"></div>
			</div>
		`;
	}

	render_exercise_alternative(question, alternative) {
		const optionLabel = this.clean(alternative.option_label);
		return `
			<label class="bruce-exercise-dialog__alternative">
				<input type="radio" name="question-${this.escape_attribute(question.name)}" value="${this.escape_attribute(optionLabel)}">
				<span><strong>${this.escape_html(optionLabel)}.</strong> ${alternative.option_text || ""}</span>
			</label>
		`;
	}

	save_exercise_answers(dialog, exerciseList, questions) {
		const selectedAnswers = questions
			.map((question) => {
				const selectedOption = dialog.$wrapper.find(`input[name="question-${this.css_escape(question.name)}"]:checked`).val();
				return {
					question: question.name,
					selected_option: selectedOption,
				};
			})
			.filter((answer) => answer.selected_option);

		if (!selectedAnswers.length) {
			frappe.msgprint(__("Selecione pelo menos uma alternativa."));
			return;
		}

		const calls = selectedAnswers.map((answer) => frappe.call({
			method: "zuno_lms.services.student_access.save_student_answer",
			args: {
				exercise_list: exerciseList.name,
				question: answer.question,
				selected_option: answer.selected_option,
			},
		}));

		Promise.all(calls).then((responses) => {
			responses.forEach((response, index) => {
				const answer = selectedAnswers[index];
				const result = response.message || {};
				const resultElement = dialog.$wrapper
					.find(`.bruce-exercise-dialog__question[data-question="${this.escape_attribute(answer.question)}"] .bruce-exercise-dialog__result`);
				resultElement
					.removeClass("text-muted text-success text-danger")
					.addClass(result.is_correct ? "text-success" : "text-danger")
					.text(result.is_correct ? __("Resposta correta.") : __("Resposta incorreta."));
			});

			frappe.show_alert({
				message: __("Respostas salvas."),
				indicator: "green",
			});
		});
	}

	render_field(label, value) {
		return `
			<div class="bruce-student-dashboard__field">
				<div class="bruce-student-dashboard__label">${this.escape_html(label)}</div>
				<div class="bruce-student-dashboard__value">${this.escape_html(this.clean(value) || __("Não informado"))}</div>
			</div>
		`;
	}

	copy_meeting_url(meetingUrl) {
		if (navigator.clipboard && window.isSecureContext) {
			navigator.clipboard.writeText(meetingUrl).then(() => {
				this.show_copy_success();
			}).catch(() => {
				this.copy_meeting_url_fallback(meetingUrl);
			});
			return;
		}

		this.copy_meeting_url_fallback(meetingUrl);
	}

	copy_meeting_url_fallback(meetingUrl) {
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

	show_manual_copy_dialog(meetingUrl) {
		frappe.msgprint({
			title: __("Copiar link da aula"),
			message: __("Não foi possível copiar automaticamente. Copie o link abaixo:") + `<br><br><code>${this.escape_html(meetingUrl)}</code>`,
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

	escape_attribute(value) {
		return this.escape_html(value);
	}

	css_escape(value) {
		if (window.CSS && window.CSS.escape) {
			return window.CSS.escape(String(value || ""));
		}

		return String(value || "").replace(/[^a-zA-Z0-9_-]/g, "\\$&");
	}

	inject_styles() {
		if ($("#bruce-student-dashboard-styles").length) {
			return;
		}

		$(`<style id="bruce-student-dashboard-styles">
			.bruce-student-dashboard__content {
				max-width: 760px;
			}

			.bruce-student-dashboard__panel {
				background: var(--card-bg);
				border: 1px solid var(--border-color);
				border-radius: 8px;
				margin-bottom: 16px;
				padding: 24px;
			}

			.bruce-student-dashboard__header {
				display: flex;
				align-items: flex-start;
				justify-content: space-between;
				gap: 16px;
				margin-bottom: 24px;
			}

			.bruce-student-dashboard__header h3 {
				margin: 4px 0 0;
			}

			.bruce-student-dashboard__section-title h3 {
				margin: 4px 0 0;
			}

			.bruce-student-dashboard__section-title {
				align-items: flex-start;
				display: flex;
				gap: 16px;
				justify-content: space-between;
			}

			.bruce-student-dashboard__grid {
				display: grid;
				grid-template-columns: repeat(2, minmax(0, 1fr));
				gap: 16px;
			}

			.bruce-student-dashboard__progress-grid {
				display: grid;
				gap: 12px;
				grid-template-columns: repeat(5, minmax(0, 1fr));
				margin-top: 16px;
			}

			.bruce-student-dashboard__metric {
				border: 1px solid var(--border-color);
				border-radius: 8px;
				min-width: 0;
				padding: 12px;
			}

			.bruce-student-dashboard__metric-value {
				font-size: 18px;
				font-weight: 600;
				overflow-wrap: anywhere;
			}

			.bruce-student-dashboard__material-list {
				display: grid;
				gap: 12px;
				margin-top: 16px;
			}

			.bruce-student-dashboard__exercise-list {
				display: grid;
				gap: 12px;
				margin-top: 16px;
			}

			.bruce-student-dashboard__material-item,
			.bruce-student-dashboard__exercise-item {
				align-items: flex-start;
				border: 1px solid var(--border-color);
				border-radius: 8px;
				display: flex;
				gap: 16px;
				justify-content: space-between;
				padding: 16px;
			}

			.bruce-student-dashboard__material-main {
				min-width: 0;
			}

			.bruce-student-dashboard__material-title {
				font-weight: 600;
				overflow-wrap: anywhere;
			}

			.bruce-student-dashboard__material-meta {
				color: var(--text-muted);
				font-size: 12px;
				margin-top: 4px;
			}

			.bruce-student-dashboard__material-grid {
				display: grid;
				gap: 12px;
				grid-template-columns: repeat(3, minmax(0, 1fr));
				margin-top: 16px;
			}

			.bruce-student-dashboard__material-action {
				flex: 0 0 auto;
			}

			.bruce-student-dashboard__exercise-main {
				min-width: 0;
			}

			.bruce-student-dashboard__field {
				min-width: 0;
			}

			.bruce-student-dashboard__label {
				color: var(--text-muted);
				font-size: 12px;
				margin-bottom: 4px;
			}

			.bruce-student-dashboard__value {
				overflow-wrap: anywhere;
			}

			.bruce-student-dashboard__actions {
				display: flex;
				flex-wrap: wrap;
				gap: 8px;
				margin-top: 24px;
			}

			.bruce-exercise-dialog {
				display: grid;
				gap: 20px;
			}

			.bruce-exercise-dialog__question {
				border-bottom: 1px solid var(--border-color);
				padding-bottom: 16px;
			}

			.bruce-exercise-dialog__question:last-child {
				border-bottom: 0;
				padding-bottom: 0;
			}

			.bruce-exercise-dialog__title {
				font-weight: 600;
				margin-bottom: 8px;
			}

			.bruce-exercise-dialog__statement {
				margin-bottom: 12px;
			}

			.bruce-exercise-dialog__alternatives {
				display: grid;
				gap: 8px;
			}

			.bruce-exercise-dialog__alternative {
				align-items: flex-start;
				display: flex;
				gap: 8px;
			}

			.bruce-exercise-dialog__result {
				margin-top: 8px;
			}

			@media (max-width: 640px) {
				.bruce-student-dashboard__panel {
					padding: 16px;
				}

				.bruce-student-dashboard__header {
					display: block;
				}

				.bruce-student-dashboard__header .indicator-pill {
					margin-top: 12px;
				}

				.bruce-student-dashboard__grid {
					grid-template-columns: 1fr;
				}

				.bruce-student-dashboard__section-title {
					display: block;
				}

				.bruce-student-dashboard__section-title .indicator-pill {
					margin-top: 12px;
				}

				.bruce-student-dashboard__progress-grid {
					grid-template-columns: 1fr 1fr;
				}

				.bruce-student-dashboard__material-item,
				.bruce-student-dashboard__exercise-item {
					display: block;
				}

				.bruce-student-dashboard__material-grid {
					grid-template-columns: 1fr;
				}

				.bruce-student-dashboard__material-action {
					margin-top: 16px;
				}
			}
		</style>`).appendTo("head");
	}
}
