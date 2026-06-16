from controllers import (
    get_register_page,
    get_request_info,
)

rotas = {
    "/register": get_register_page,
    "/request/info": get_request_info,
}
