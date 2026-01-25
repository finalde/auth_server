"""Utility for converting IdPyOIDC responses to FastAPI responses."""

from typing import Any, Dict

from fastapi.responses import JSONResponse, RedirectResponse, Response


class OIDCResponseConverter:
    """Utility class for converting IdPyOIDC responses to FastAPI responses."""

    @staticmethod
    def convert_to_dict(response: Any) -> Dict[str, Any]:
        """Convert IdPyOIDC response to dict."""
        if hasattr(response, "to_dict"):
            return response.to_dict()
        elif isinstance(response, dict):
            return dict(response)
        elif hasattr(response, "__dict__"):
            return {
                k: v
                for k, v in response.__dict__.items()
                if not k.startswith("_")
            }
        else:
            return {"response": str(response)}

    @staticmethod
    def convert_authorization_response(
        response: Any, request_data: Dict[str, Any]
    ) -> Response:
        """Convert IdPyOIDC authorization response to FastAPI response."""
        # Handle dict with response_args and return_uri
        if isinstance(response, dict) and "response_args" in response and "return_uri" in response:
            return OIDCResponseConverter._handle_response_args_dict(response)

        # Convert to dict
        resp_dict = OIDCResponseConverter.convert_to_dict(response)

        # Handle error response
        if "error" in resp_dict:
            return OIDCResponseConverter._handle_error_response(resp_dict, request_data)

        # Handle success response with code
        redirect_uri = request_data.get("redirect_uri")
        if redirect_uri and "code" in resp_dict:
            return OIDCResponseConverter._handle_success_redirect(resp_dict, redirect_uri)

        # Fallback: return as JSON
        return JSONResponse(content=resp_dict)

    @staticmethod
    def _handle_response_args_dict(response: Dict[str, Any]) -> RedirectResponse:
        """Handle response with response_args and return_uri."""
        from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

        response_args = response.get("response_args")
        return_uri = response.get("return_uri")

        # Convert response_args to dict
        if hasattr(response_args, "to_dict"):
            args_dict = response_args.to_dict()
        elif isinstance(response_args, dict):
            args_dict = dict(response_args)
        else:
            try:
                args_dict = {k: v for k, v in response_args.items()}
            except Exception:
                args_dict = {"response": str(response_args)}

        # Merge with existing query string
        parsed = urlparse(return_uri)
        existing_qs = dict(parse_qsl(parsed.query))
        merged_qs = {**existing_qs, **args_dict}
        new_query = urlencode(merged_qs)
        new_url = urlunparse(parsed._replace(query=new_query))

        return RedirectResponse(url=new_url, status_code=302)

    @staticmethod
    def _handle_error_response(
        resp_dict: Dict[str, Any], request_data: Dict[str, Any]
    ) -> Response:
        """Handle error response."""
        from urllib.parse import urlencode

        redirect_uri = request_data.get("redirect_uri")
        if redirect_uri:
            error_params = {"error": resp_dict.get("error")}
            if "error_description" in resp_dict:
                error_params["error_description"] = resp_dict["error_description"]
            if request_data.get("state"):
                error_params["state"] = request_data["state"]
            redirect_url = f"{redirect_uri}?{urlencode(error_params)}"
            return RedirectResponse(url=redirect_url, status_code=302)
        return JSONResponse(status_code=400, content=resp_dict)

    @staticmethod
    def _handle_success_redirect(
        resp_dict: Dict[str, Any], redirect_uri: str
    ) -> RedirectResponse:
        """Handle success redirect with authorization code."""
        from urllib.parse import urlencode

        success_params = {"code": resp_dict["code"]}
        if "state" in resp_dict:
            success_params["state"] = resp_dict["state"]
        redirect_url = f"{redirect_uri}?{urlencode(success_params)}"
        return RedirectResponse(url=redirect_url, status_code=302)

    @staticmethod
    def convert_token_response(response: Any) -> JSONResponse:
        """Convert IdPyOIDC token response to FastAPI JSONResponse."""
        # Extract response content
        if isinstance(response, dict):
            if "response_args" in response:
                response_content = response["response_args"]
            elif "response" in response:
                response_content = response["response"]
            else:
                response_content = response
        elif hasattr(response, "to_dict"):
            response_content = response.to_dict()
        elif hasattr(response, "__dict__"):
            response_content = dict(response.__dict__)
        else:
            response_content = {"response": str(response)}

        # Ensure it's a dict
        if not isinstance(response_content, dict):
            response_content = {"response": str(response_content)}

        # Handle errors
        if "error" in response_content:
            error_code = response_content.get("error", "invalid_request")
            if error_code in ["invalid_client", "invalid_grant", "unauthorized_client"]:
                status_code = 401
            elif error_code == "server_error":
                status_code = 500
            else:
                status_code = 400
            return JSONResponse(status_code=status_code, content=response_content)

        return JSONResponse(content=response_content)
