import requests

from django import urls


class UsageCartData:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_usage_change"))
        resp = requests.get(api_url, cookies=self.request.COOKIES)
        if resp.status_code != 200:
            return context
        context.update(resp.json())
        return context
