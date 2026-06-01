frappe.pages["bruce-live-room"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Aula ao vivo"),
		single_column: true,
	});

	page.main.addClass("bruce-live-room");
	const liveRoom = new BruceLiveRoom(page);

	page.set_primary_action(__("Atualizar"), () => liveRoom.load(), "refresh");
	liveRoom.load();
};

frappe.pages["bruce-live-room"].on_page_show = function (wrapper) {
	if (wrapper.bruce_live_room) {
		wrapper.bruce_live_room.load();
	}
};

class BruceLiveRoom {
	constructor(page) {
		this.page = page;
		this.container = $('<div class="bruce-live-room__content"></div>').appendTo(page.main);
		this.api = null;
		this.scriptPromise = null;
		if (page.wrapper && page.wrapper.addClass) {
			page.wrapper.addClass("bruce-live-room-page");
		}
		this.inject_styles();
		const wrapper = page.wrapper && page.wrapper.get ? page.wrapper.get(0) : page.wrapper;
		if (wrapper) {
			wrapper.bruce_live_room = this;
		}
	}

	load() {
		const liveClass = this.get_live_class_from_route();
		this.dispose_jitsi();

		if (!liveClass) {
			this.render_error(__("Aula não informada."), __("Abra a aula a partir da página Minha Aula ou do Painel do Professor."));
			return;
		}

		this.render_loading();
		frappe.call({
			method: "bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.get_live_room_context",
			args: {
				live_class: liveClass,
			},
			callback: (response) => {
				const context = response.message || {};
				this.render_room(context);
				this.load_jitsi(context);
			},
			error: () => {
				this.render_error(__("Não foi possível abrir a aula."), __("Confira seu acesso ou tente novamente em alguns instantes."));
			},
		});
	}

	get_live_class_from_route() {
		if (frappe.route_options && frappe.route_options.live_class) {
			return this.clean(frappe.route_options.live_class);
		}

		const route = frappe.get_route ? frappe.get_route() : [];
		return this.clean(route[1]);
	}

	render_loading() {
		this.container.html(`
			<div class="bruce-live-room__panel">
				<div class="text-muted">${this.escape_html(__("Carregando aula ao vivo..."))}</div>
			</div>
		`);
	}

	render_error(title, message) {
		this.container.html(`
			<div class="bruce-live-room__panel">
				<h3>${this.escape_html(title)}</h3>
				<p class="text-muted mb-0">${this.escape_html(message)}</p>
			</div>
		`);
	}

	render_room(context) {
		const courseDisplay = this.clean(context.course_title) || this.clean(context.course);
		const batchDisplay = this.clean(context.batch_title) || this.clean(context.batch);
		const statusLabel = this.clean(context.status_label) || this.clean(context.status);
		const externalUrl = this.clean(context.external_url);

		this.container.html(`
			<div class="bruce-live-room__shell">
				<div class="bruce-live-room__header">
					<div>
						<div class="text-muted">${this.escape_html(__("Aula ao vivo"))}</div>
						<h3>${this.escape_html(this.clean(context.title) || __("Sem título"))}</h3>
					</div>
					<div class="bruce-live-room__header-actions">
						<span class="indicator-pill ${this.get_class_status_indicator(context.status)}">
							${this.escape_html(statusLabel || __("Sem status"))}
						</span>
						<button class="btn btn-default btn-sm bruce-live-room__external" ${externalUrl ? "" : "disabled"}>
							${this.escape_html(__("Abrir em nova aba"))}
						</button>
					</div>
				</div>
				<div class="bruce-live-room__grid">
					${this.render_field(__("Curso"), courseDisplay)}
					${this.render_field(__("Turma"), batchDisplay)}
					${this.render_field(__("Data e horário"), this.format_datetime(context.starts_at))}
					${this.render_field(__("Status"), statusLabel)}
				</div>
				<div class="bruce-live-room__stage">
					<div class="bruce-live-room__jitsi" id="bruce-live-room-jitsi">
						<div class="text-muted">${this.escape_html(__("Preparando sala..."))}</div>
					</div>
				</div>
			</div>
		`);

		this.container.find(".bruce-live-room__external").on("click", () => {
			if (externalUrl) {
				window.open(externalUrl, "_blank", "noopener");
			}
		});
	}

	load_jitsi(context) {
		const domain = this.clean(context.domain);
		const roomName = this.clean(context.room_name);
		const parentNode = this.container.find("#bruce-live-room-jitsi").get(0);

		if (!domain || !roomName || !parentNode) {
			this.render_jitsi_error(__("Sala Jitsi indisponível."));
			return;
		}

		this.load_external_api(domain).then(() => {
			if (!window.JitsiMeetExternalAPI) {
				this.render_jitsi_error(__("Não foi possível carregar o Jitsi."));
				return;
			}

			parentNode.innerHTML = "";
			this.api = new window.JitsiMeetExternalAPI(domain, {
				roomName,
				parentNode,
				width: "100%",
				height: "100%",
				userInfo: {
					displayName: frappe.session.user_fullname || frappe.session.user,
				},
				configOverwrite: {
					prejoinPageEnabled: true,
				},
				interfaceConfigOverwrite: {
					MOBILE_APP_PROMO: false,
				},
			});
		}).catch(() => {
			this.render_jitsi_error(__("Não foi possível carregar o Jitsi. Use o botão Abrir em nova aba."));
		});
	}

	load_external_api(domain) {
		if (window.JitsiMeetExternalAPI) {
			return Promise.resolve();
		}

		if (this.scriptPromise) {
			return this.scriptPromise;
		}

		this.scriptPromise = new Promise((resolve, reject) => {
			const script = document.createElement("script");
			script.src = `https://${domain}/external_api.js`;
			script.async = true;
			script.onload = resolve;
			script.onerror = reject;
			document.head.appendChild(script);
		});

		return this.scriptPromise;
	}

	render_jitsi_error(message) {
		const target = this.container.find("#bruce-live-room-jitsi");
		target.html(`<div class="bruce-live-room__jitsi-error">${this.escape_html(message)}</div>`);
	}

	dispose_jitsi() {
		if (this.api && this.api.dispose) {
			this.api.dispose();
		}
		this.api = null;
	}

	render_field(label, value) {
		return `
			<div class="bruce-live-room__field">
				<div class="bruce-live-room__label">${this.escape_html(label)}</div>
				<div class="bruce-live-room__value">${this.escape_html(this.clean(value) || __("Não informado"))}</div>
			</div>
		`;
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
		if ($("#bruce-live-room-styles").length) {
			return;
		}

		$(`<style id="bruce-live-room-styles">
			.bruce-live-room-page .page-head {
				min-height: 42px;
			}

			.bruce-live-room-page .page-head .page-title {
				padding: 8px 0;
			}

			.bruce-live-room-page .layout-main-section {
				padding-top: 0;
			}

			.bruce-live-room__content {
				margin: 0 auto;
				max-width: 1380px;
				min-height: calc(100vh - 56px);
				padding: 12px 16px 16px;
				width: 100%;
			}

			.bruce-live-room__panel {
				background: var(--card-bg);
				border: 1px solid var(--border-color);
				border-radius: 8px;
				padding: 20px;
			}

			.bruce-live-room__shell {
				display: flex;
				flex-direction: column;
				gap: 10px;
				min-height: calc(100vh - 96px);
			}

			.bruce-live-room__header {
				background: var(--card-bg);
				border: 1px solid var(--border-color);
				border-radius: 8px;
				display: flex;
				align-items: center;
				justify-content: space-between;
				gap: 12px;
				padding: 10px 12px;
			}

			.bruce-live-room__header h3 {
				margin: 4px 0 0;
				font-size: 20px;
				line-height: 1.25;
			}

			.bruce-live-room__header-actions {
				align-items: center;
				display: flex;
				flex-shrink: 0;
				flex-wrap: wrap;
				gap: 8px;
				justify-content: flex-end;
			}

			.bruce-live-room__grid {
				background: var(--subtle-fg, var(--card-bg));
				border: 1px solid var(--border-color);
				border-radius: 8px;
				display: grid;
				grid-template-columns: repeat(4, minmax(0, 1fr));
				gap: 8px;
				padding: 8px 10px;
			}

			.bruce-live-room__label {
				color: var(--text-muted);
				font-size: 12px;
				line-height: 1.2;
				margin-bottom: 2px;
			}

			.bruce-live-room__value {
				font-size: 13px;
				line-height: 1.25;
				overflow-wrap: anywhere;
			}

			.bruce-live-room__actions {
				display: flex;
				flex-wrap: wrap;
				gap: 8px;
				margin-top: 16px;
			}

			.bruce-live-room__stage {
				background: #111827;
				border: 1px solid var(--border-color);
				border-radius: 8px;
				height: calc(100vh - 220px);
				min-height: 520px;
				overflow: hidden;
			}

			.bruce-live-room__jitsi {
				align-items: center;
				display: flex;
				height: 100%;
				justify-content: center;
				width: 100%;
			}

			.bruce-live-room__jitsi iframe {
				border: 0;
			}

			.bruce-live-room__jitsi-error {
				color: #fff;
				padding: 24px;
				text-align: center;
			}

			@media (max-width: 900px) {
				.bruce-live-room__grid {
					grid-template-columns: repeat(2, minmax(0, 1fr));
				}

				.bruce-live-room__stage {
					height: calc(100vh - 240px);
				}
			}

			@media (max-width: 640px) {
				.bruce-live-room__content {
					padding: 8px 8px 12px;
				}

				.bruce-live-room__panel {
					padding: 16px;
				}

				.bruce-live-room__header {
					align-items: flex-start;
					flex-direction: column;
				}

				.bruce-live-room__header h3 {
					font-size: 18px;
				}

				.bruce-live-room__header-actions {
					justify-content: flex-start;
					width: 100%;
				}

				.bruce-live-room__grid {
					grid-template-columns: 1fr;
				}

				.bruce-live-room__stage {
					height: 70vh;
					min-height: 360px;
				}
			}
		</style>`).appendTo("head");
	}
}
