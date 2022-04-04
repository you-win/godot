#include "redirect.h"
#include "core/object.h"
#include "core/print_string.h"

void Redirect::_print_handler(void *p_this, const String &p_string, bool p_error) {
	Redirect *r = (Redirect *)p_this;
	r->emit_signal("print_line", p_string, p_error);
}

void Redirect::_bind_methods() {
	ADD_SIGNAL(MethodInfo("print_line", PropertyInfo(Variant::STRING, "text"), PropertyInfo(Variant::BOOL, "is_error")));
}

Redirect *Redirect::singleton = nullptr;

Redirect *Redirect::get_singleton() {
	return singleton;
}

Redirect *Redirect::create() {
	ERR_FAIL_COND_V_MSG(singleton, nullptr, "Redirect singleton already exists.");
	return memnew(Redirect);
}

Redirect::Redirect() {
	singleton = this;

	print_handler.printfunc = _print_handler;
	print_handler.userdata = this;
	add_print_handler(&print_handler);
}

Redirect::~Redirect() {
	remove_print_handler(&print_handler);
}
