from .api_chart_data import APIChartDataView
from .api_source_item_autocomplete_search import APISourceItemAutocompleteSearchView
from .api_source_item_orders import APISourceItemOrdersView
from .api_source_item_quantity_adjustment import APISourceItemQuantityAdjustmentView
from .api_source_item_wide_filter import APISourceItemWideFilterView
from .reports_created_today import ReportsCreatedTodayView
from .reports_price_over_time import ReportsPriceOverTimeView
from .source_item_create import SourceItemCreateView
from .source_item_order_items import SourceItemOrderItemsView
from .source_item_orders import SourceItemOrdersView
from .source_item_search import SourceItemSearchView
from .stats import SourceItemStatsView

# TODO: Try to do similar to v3old: http://localhost:8080/incoming/group/[uuid]/ex_edit
