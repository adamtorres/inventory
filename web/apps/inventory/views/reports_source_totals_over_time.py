from django.views import generic

from scrap import utils

from inventory import reports as inv_reports


class ReportsSourceTotalsOverTimeView(generic.TemplateView):
    template_name = "inventory/reports_source_totals_over_time.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tall_data = inv_reports.SourceTotalsOverTime.run()
        headers = ["year/month"]
        headers_set = False
        cur_year_month = None
        wide_data = []
        wide_row = []
        for row in tall_data:
            if cur_year_month is None:
                cur_year_month = row["year_month"]
                wide_row.append(row["year_month"])
            if cur_year_month != row["year_month"]:
                headers_set = True
                wide_data.append(wide_row)
                wide_row = [row["year_month"]]
                cur_year_month = row["year_month"]
            if not headers_set:
                # headers.extend([f"{row["iname"]} orders", f"{row["iname"]} items", f"{row["iname"]} total cost"])
                headers.extend([f"{row["iname"]}"])
            wide_row.append({"orders": row["orders"], "items": row["items"], "total_cost": row["total_cost"]})
        wide_data.append(wide_row)
        wide_data.reverse()
        context['source_totals_over_time'] = wide_data
        context['headers'] = headers
        return context
