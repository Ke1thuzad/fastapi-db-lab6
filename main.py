from fastapi import FastAPI

from routers import users, couriers, order_contents, orders, views, funcs_procs, reports

app = FastAPI()

app.include_router(users.router)
app.include_router(couriers.router)
app.include_router(orders.router)
app.include_router(order_contents.router)
app.include_router(views.router)
app.include_router(funcs_procs.router)
app.include_router(reports.router)
