"""Cliente de API para el escritorio Hamelín RH.

Comunica la aplicación de escritorio con la API privada FastAPI mediante HTTP.
Gestiona el token JWT, la expiración de sesión y los reintentos ante fallos de
conexión. No expone credenciales en logs.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from app.models import Token


class ApiClientError(Exception):
    """Error genérico de cliente de API."""


class AuthError(ApiClientError):
    """Error de autenticación (401/403)."""


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self._token: Optional[str] = None
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    # ------------------------------------------------------------------ token

    def set_token(self, token: Optional[str]) -> None:
        self._token = token
        if token:
            self._client.headers["Authorization"] = f"Bearer {token}"
        else:
            self._client.headers.pop("Authorization", None)

    def get_token(self) -> Optional[str]:
        return self._token

    def clear_token(self) -> None:
        self._token = None
        self._client.headers.pop("Authorization", None)

    @property
    def headers(self) -> Dict[str, str]:
        return dict(self._client.headers)

    # ------------------------------------------------------------------ peticiones

    def _url(self, path: str) -> str:
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _headers(self) -> Dict[str, str]:
        h = {}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _manejar_respuesta(self, resp: httpx.Response) -> Any:
        if resp.status_code in (401, 403):
            raise AuthError(resp.json().get("detail", "Acceso denegado") if resp.headers.get("content-type", "").startswith("application/json") else "Acceso denegado")
        if resp.status_code >= 400:
            detalle = resp.text
            try:
                detalle = resp.json().get("detail", resp.text)
            except Exception:
                pass
            raise ApiClientError(f"Error {resp.status_code}: {detalle}")
        if resp.status_code == 204:
            return None
        return resp.json()

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        resp = self._client.get(self._url(path), params=params, headers=self._headers())
        return self._manejar_respuesta(resp)

    def post(self, path: str, json: Optional[Dict] = None, data: Optional[Dict] = None,
             params: Optional[Dict] = None) -> Any:
        resp = self._client.post(self._url(path), json=json, data=data, params=params,
                                 headers=self._headers())
        return self._manejar_respuesta(resp)

    def patch(self, path: str, json: Optional[Dict] = None,
              params: Optional[Dict] = None) -> Any:
        resp = self._client.patch(self._url(path), json=json, params=params,
                                  headers=self._headers())
        return self._manejar_respuesta(resp)

    def delete(self, path: str) -> Any:
        resp = self._client.delete(self._url(path), headers=self._headers())
        return self._manejar_respuesta(resp)

    def login(self, username: str, password: str) -> Token:
        datos = self.post("/api/v1/auth/login", json={"username": username, "password": password})
        token = Token(**datos)
        self.set_token(token.access_token)
        return token

    def close(self) -> None:
        self._client.close()
