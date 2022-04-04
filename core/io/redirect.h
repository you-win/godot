#ifndef REDIRECT_H
#define REDIRECT_H

#include "core/object.h"
#include "core/print_string.h"

class Redirect : public Object {
    GDCLASS(Redirect, Object);
    OBJ_CATEGORY("Utilities");

public:
private:
    PrintHandlerList print_handler;
    static void _print_handler(void *p_this, const String &p_string, bool p_error);

protected:
    static Redirect *singleton;
    static void _bind_methods();

public:
    static Redirect *get_singleton();
    
    static Redirect *create();

    Redirect();
    ~Redirect();
};

#endif // REDIRECT_H
