from .api_chart_data import APIChartDataView
from .api_saved_search import APISavedSearchView
from .api_source_item_autocomplete_search import APISourceItemAutocompleteSearchView
from .api_source_item_orders import APISourceItemOrdersView
from .api_source_item_quantity_adjustment import APISourceItemQuantityAdjustmentView
from .api_source_item_wide_filter import APISourceItemWideFilterView
from .reports_common_name_prices import ReportsCommonNamePricesView
from .reports_created_today import ReportsCreatedTodayView
from .reports_debug_source_item_list import ReportsDebugSourceItemListView
from .reports_duplicate_items import ReportsDuplicateItemsView
from .reports_orders_created_range import ReportsOrdersCreatedRangeView
from .reports_order_created_times_last_week import ReportsCreatedTimesLastWeekView
from .reports_packaging_costs import ReportsPackagingCostsView
from .reports_price_over_time import ReportsPriceOverTimeView
from .reports_source_categories import ReportsSourceCategoriesView
from .reports_source_totals import ReportsSourceTotalsView
from .reports_source_totals_over_time import ReportsSourceTotalsOverTimeView
from .search_criteria import SearchCriteriaCurrentPricesView
from .source_item_create import SourceItemCreateView
from .source_item_math_check import SourceItemMathCheckView
from .source_item_order_items import SourceItemOrderItemsView
from .source_item_orders import SourceItemOrdersView
from .source_item_search import SourceItemSaveSearchView, SourceItemSearchView
from .stats import SourceItemStatsView

# TODO: Try to do similar to v3old: http://localhost:8080/incoming/group/[uuid]/ex_edit
