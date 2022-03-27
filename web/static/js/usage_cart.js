// <span>Items: </span><span data-field="used_items">0</span>
// <span>Units: </span><span data-field="total_used_units">0</span>
function update_cart_header(data) {
    // if data does not have total_used_units: exit
    if (!('total_used_units' in data)) {
        // Set empty defaults
        data["total_used_units"] = 0;
        data["used_items"] = [];
    }
    let cart_div = $("#usage-cart-header");
    cart_div.find('[data-field]').each(function() {
        let e = $(this);
        let key = e.data('field');
        if (key === "total_used_units") {
            e.text(data[key]);
        }
        if (key === "used_items") {
            e.text(data[key].length);
        }
    });
}

function update_cart() {
    var jqxhr = $.get({
        url: "/inventory/api_usage_change/",
    })
    .done(function(e) {
        update_cart_header(e);
    })
    .fail(function() {
        logit("update_cart fail");
    })
    .always(function() {
    });

}

$( document ).ready(function() {
    update_cart();
});
