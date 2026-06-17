from controllers import (
    get_home_page,
    get_register_page,
    post_register,
    get_login_page,
    post_login,
    get_dashboard,
    get_admin,
    get_logout,
)

rotas = {
    ("GET",  "/"):          get_home_page,
    ("GET",  "/register"):  get_register_page,
    ("POST", "/register"):  post_register,
    ("GET",  "/login"):     get_login_page,
    ("POST", "/login"):     post_login,
    ("GET",  "/dashboard"): get_dashboard,
    ("GET",  "/admin"):     get_admin,
    ("GET",  "/logout"):    get_logout,
}
