from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if hasattr(request.user, 'profile') and request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes permiso para acceder a esta página.')
            return redirect('home')
        return wrapped
    return decorator

admin_required = role_required(['admin'])
gestor_required = role_required(['admin', 'gestor'])
