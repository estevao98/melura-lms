frappe.listview_settings["Melura Live Class"] = {
	onload(listview) {
		set_live_class_list_title(listview);
	},
	refresh(listview) {
		set_live_class_list_title(listview);
	},
};

function set_live_class_list_title(listview) {
	if (!listview.page || !listview.page.set_title) {
		return;
	}

	listview.page.set_title(__("Lista de aulas ao vivo"));
}
