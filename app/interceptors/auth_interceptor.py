import grpc
from app.utils.jwt_utils import verify_jwt_token


class AuthServerInterceptor(grpc.ServerInterceptor):
    PUBLIC_METHODS = []

    def intercept_service(self, continuation, handler_call_details):
        if handler_call_details.method in self.PUBLIC_METHODS:
            return continuation(handler_call_details)

        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get("authorization", "").replace("Bearer ", "")

        if not token:
            def deny_handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing token")
            return grpc.unary_unary_rpc_method_handler(deny_handler)

        try:
            payload, error = verify_jwt_token(token)
            if error:
                def deny_handler(request, context):
                    context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
                return grpc.unary_unary_rpc_method_handler(deny_handler)

            return continuation(handler_call_details)
        except Exception:
            def deny_handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token validation failed")
            return grpc.unary_unary_rpc_method_handler(deny_handler)


