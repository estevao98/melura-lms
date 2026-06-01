(function () {
	var themeStorageKey = "bruceStudentPortalTheme";
	var menu = document.querySelector("[data-student-menu]");
	var backdrop = document.querySelector("[data-student-menu-backdrop]");
	var toggleButton = document.querySelector("[data-student-menu-toggle]");
	var themeToggle = document.querySelector("[data-student-theme-toggle]");
	var themeLabel = document.querySelector("[data-student-theme-label]");
	var themeButtons = document.querySelectorAll("[data-student-theme-option]");
	var currentTheme = null;

	function getPreferredTheme() {
		var savedTheme = null;

		try {
			savedTheme = window.localStorage.getItem(themeStorageKey);
		} catch (error) {
			savedTheme = null;
		}

		if (savedTheme === "light" || savedTheme === "dark") {
			return savedTheme;
		}

		return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
	}

	function setTheme(theme, persist) {
		if (theme !== "light" && theme !== "dark") {
			return;
		}

		document.documentElement.setAttribute("data-bruce-theme", theme);
		currentTheme = theme;

		if (themeToggle) {
			themeToggle.setAttribute("aria-label", theme === "dark" ? "Ativar tema claro" : "Ativar tema escuro");
			themeToggle.setAttribute("title", theme === "dark" ? "Ativar tema claro" : "Ativar tema escuro");
		}

		if (themeLabel) {
			themeLabel.textContent = theme === "dark" ? "Claro" : "Escuro";
		}

		themeButtons.forEach(function (button) {
			button.setAttribute("aria-pressed", button.getAttribute("data-student-theme-option") === theme ? "true" : "false");
		});

		if (!persist) {
			return;
		}

		try {
			window.localStorage.setItem(themeStorageKey, theme);
		} catch (error) {
			showMessage("Não foi possível salvar a preferência de tema neste navegador.");
		}
	}

	function showMessage(message) {
		var existing = document.querySelector("[data-student-copy-message]");
		if (existing) {
			existing.remove();
		}

		var element = document.createElement("div");
		element.setAttribute("data-student-copy-message", "true");
		element.className = "bruce-student-portal__card";
		element.textContent = message;

		var portal = document.querySelector("[data-student-portal]");
		if (portal) {
			portal.insertBefore(element, portal.firstChild.nextSibling);
		}

		window.setTimeout(function () {
			element.remove();
		}, 3000);
	}

	function setMenuOpen(isOpen) {
		if (!menu || !backdrop || !toggleButton) {
			return;
		}

		menu.hidden = !isOpen;
		backdrop.hidden = !isOpen;
		document.body.classList.toggle("bruce-student-portal-menu-open", isOpen);
		toggleButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
		toggleButton.setAttribute("aria-label", isOpen ? "Fechar menu" : "Abrir menu");
	}

	function closeMenu() {
		setMenuOpen(false);
	}

	function isMenuOpen() {
		return Boolean(menu && !menu.hidden);
	}

	function copyFallback(text) {
		var textarea = document.createElement("textarea");
		textarea.value = text;
		textarea.setAttribute("readonly", "");
		textarea.style.position = "fixed";
		textarea.style.opacity = "0";
		document.body.appendChild(textarea);
		textarea.select();

		try {
			if (document.execCommand("copy")) {
				showMessage("Link da aula copiado.");
				return;
			}
		} catch (error) {
			// The manual prompt below is safer than exposing implementation details.
		} finally {
			document.body.removeChild(textarea);
		}

		window.prompt("Copie o link da aula:", text);
	}

	if (toggleButton) {
		toggleButton.addEventListener("click", function () {
			setMenuOpen(toggleButton.getAttribute("aria-expanded") !== "true");
		});
	}

	if (themeToggle) {
		themeToggle.addEventListener("click", function () {
			setTheme(currentTheme === "dark" ? "light" : "dark", true);
		});
	}

	themeButtons.forEach(function (button) {
		button.addEventListener("click", function () {
			setTheme(button.getAttribute("data-student-theme-option"), true);
		});
	});

	document.addEventListener("click", function (event) {
		if (event.target.closest("[data-student-menu-close]") || event.target.closest("[data-student-menu-backdrop]")) {
			closeMenu();
			return;
		}

		var menuItem = event.target.closest("[data-student-menu-item]");
		if (!menuItem) {
			if (isMenuOpen() && !event.target.closest("[data-student-menu]") && !event.target.closest("[data-student-menu-toggle]")) {
				closeMenu();
			}
			return;
		}

		if (menuItem.hasAttribute("data-student-support-placeholder")) {
			event.preventDefault();
			showMessage("O canal de suporte ainda não foi configurado.");
		}

		closeMenu();
	});

	document.addEventListener("keydown", function (event) {
		if (event.key === "Escape") {
			closeMenu();
		}
	});

	document.addEventListener("click", function (event) {
		var button = event.target.closest("[data-copy-link]");
		if (!button) {
			return;
		}

		var link = button.getAttribute("data-copy-link");
		if (!link) {
			return;
		}

		if (navigator.clipboard && window.isSecureContext) {
			navigator.clipboard.writeText(link).then(function () {
				showMessage("Link da aula copiado.");
			}).catch(function () {
				copyFallback(link);
			});
			return;
		}

		copyFallback(link);
	});

	setTheme(getPreferredTheme(), false);
}());
