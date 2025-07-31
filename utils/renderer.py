from typing import Any, Dict, Optional

from rest_framework import renderers


class ResponseRenderer(renderers.JSONRenderer):
    def render(
        self,
        data: Dict[str, Any] | str,
        accepted_media_type: Optional[str] = None,
        renderer_context: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Render `data` into JSON, returning a bytestring.
        """
        response = renderer_context["response"]
        context = {}
        context.setdefault("error", None)
        context.setdefault("message", "Success")
        if response.exception:
            context.update(
                {
                    "error": data,
                    "status": getattr(response, "status_text", "Error"),
                    "message": "Failed",
                }
            )
        else:
            context["data"] = data
        return super().render(context, accepted_media_type, renderer_context) 