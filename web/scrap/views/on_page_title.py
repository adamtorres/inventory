class OnPageTitleMixin:
    on_page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["on_page_title"] = self.on_page_title or ""
        return context
