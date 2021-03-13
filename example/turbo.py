from django.template.response import TemplateResponse


class TurboMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_turbo = False
        request.is_turbo_frame = False
        request.is_turbo_stream = False
        request.turbo_frame = request.headers.get("turbo-frame")

        accept = request.headers.get("accept")
        if request.turbo_frame or "text/vnd.turbo-frame.html" in accept:
            request.is_turbo = True
            request.is_turbo_frame = True
        elif "text/vnd.turbo-stream.html" in accept:
            request.is_turbo = True
            request.is_turbo_stream = True

        response = self.get_response(request)

        if request.is_turbo:
            # Set status code
            if response.status_code >= 300 and response.status_code < 400:
                response.status_code = 303  # See Other
            elif response.status_code >= 400 and response.status_code < 500:
                response.status_code = 422  # Unprocessable Entity

            # Set content type
            if request.is_turbo_frame:
                response["Content-Type"] = "text/vnd.turbo-frame.html"
            elif request.is_turbo_stream:
                response["Content-Type"] = "text/vnd.turbo-stream.html"

        return response


class TurboViewMixin:
    partial_template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["include_turbo_stream"] = self.request.is_turbo_stream
        return context

    def get_partial_template_name(self):
        if self.partial_template_name:
            return self.partial_template_name

        template_names = super().get_template_names()  # NOTE uses 'super' not 'self'
        if template_names:
            before, separator, after = template_names[0].rpartition("/")
            return f"{before}{separator}_{after}"

        return None

    def get_template_names(self):
        if self.request.is_turbo:
            return [self.get_partial_template_name()]
        else:
            return super().get_template_names()


class TurboFormSuccessViewMixin:
    def get_success_template_name(self):
        """
        Return a name of success template.
        To disable use of the template set `success_template_name` as None.
        In that case the original HttpResponseRedirect is returned.
        """
        if hasattr(self, "success_template_name"):
            return self.success_template_name

        template_name = self.get_partial_template_name()
        if template_name:
            before, separator, after = template_name.rpartition(".")
            return f"{before}_success{separator}{after}"

        return None

    def get_success_context_data(self):
        return self.get_context_data()


class TurboFormViewMixin(TurboFormSuccessViewMixin, TurboViewMixin):
    def form_invalid(self, form):
        """
        Response with status code "422 Unprocessable Entity".
        """
        response = super().form_invalid(form)
        if self.request.is_turbo:
            response.status_code = 422  # Unprocessable Entity
        return response

    def form_valid(self, form):
        """
        Return a success template if this request is made by Turbo.
        """
        response = super().form_valid(form)
        success_template_name = self.get_success_template_name()
        if self.request.is_turbo and success_template_name:
            context = self.get_success_context_data()
            response = TemplateResponse(self.request, success_template_name, context)
        return response


class TurboDeleteViewMixin(TurboFormSuccessViewMixin, TurboViewMixin):
    def delete(self, request, *args, **kwargs):
        """
        Delete object and return a success template if this request is made by Turbo.
        """
        # We need to get the object ID before deleting the object as
        # it's needed in success template.
        self.object = self.get_object()
        context = self.get_success_context_data()

        # This should delete the object and return a HttpResponseRedirect
        response = super().delete(request, *args, **kwargs)

        success_template_name = self.get_success_template_name()
        if request.is_turbo and success_template_name:
            return TemplateResponse(request, success_template_name, context)

        return response

    def get_success_context_data(self):
        context = super().get_success_context_data()
        context["object"] = self.object
        context["object_id"] = self.object.pk
        return context
