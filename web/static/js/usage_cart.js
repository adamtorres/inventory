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
    cart_div.data('used_items', data['used_items']);
}

function update_cart() {
    var jqxhr = $.get({
        url: "/inventory/api_usage_change/",
    })
    .done(function(e) {
        update_cart_header(e);
        pulse_used_cart_header_start();
    })
    .fail(function() {
        logit("update_cart fail");
    })
    .always(function() {
    });

}

function get_cached_used_items() {
    let cart_div = $("#usage-cart-header");
    return cart_div.data('used_items');
}


function pulse_used_cart_header_start() {
    $("#usage-cart-header").addClass("pulse-used-cart-header");
    setTimeout(pulse_used_cart_header_stop, 2000);
}
function pulse_used_cart_header_stop() {
    $(".pulse-used-cart-header").removeClass("pulse-used-cart-header");
}
$( document ).ready(function() {
    update_cart();
});
