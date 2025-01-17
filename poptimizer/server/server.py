"""Сервер, показывающий SPA Frontend."""
import asyncio
import logging

from aiohttp import web

from poptimizer.data.edit import dividends
from poptimizer.portfolio.edit import accounts, portfolio, selected
from poptimizer.server import logger, middleware, views


class Server:
    """Сервер, показывающий SPA Frontend и отвечающий на Backend запросы.

    Реализует протокол сервиса, останавливающегося после завершения события.
    """

    def __init__(  # noqa: WPS211
        self,
        host: str,
        port: int,
        selected_srv: selected.Service,
        accounts_srv: accounts.Service,
        portfolio_srv: portfolio.Service,
        dividends_srv: dividends.Service,
    ):
        self._logger = logging.getLogger("Server")
        self._host = host
        self._port = port

        self._selected_srv = selected_srv
        self._accounts_srv = accounts_srv
        self._portfolio_srv = portfolio_srv
        self._dividends_srv = dividends_srv

    async def run(self, stop_event: asyncio.Event) -> None:
        """Запускает сервер и останавливает его после завершения события."""
        app = await self._prepare_app()

        runner = web.AppRunner(
            app,
            handle_signals=False,
            access_log_class=logger.AccessLogger,
            access_log=self._logger,
        )
        await runner.setup()
        site = web.TCPSite(
            runner,
            self._host,
            self._port,
        )

        await site.start()

        self._logger.info(
            f"started on http://{self._host}:{self._port} - press CTRL+C to quit",
        )

        await stop_event.wait()

        await runner.cleanup()

        self._logger.info("shutdown completed")

    async def _prepare_app(self) -> web.Application:
        app = web.Application(middlewares=[middleware.set_start_time_and_headers, middleware.error])

        views.Selected.register(app, self._selected_srv)
        views.Accounts.register(app, self._accounts_srv)
        views.Portfolio.register(app, self._portfolio_srv)
        views.Dividends.register(app, self._dividends_srv)
        views.Frontend.register(app)

        return app
