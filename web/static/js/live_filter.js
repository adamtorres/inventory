// #result-list == parent element to contain the filtered results

var filter_url = "set from page as it likely uses django template tags.";
var filter_fields = ["list", "of", "fields", "to", "include", "in", "filtered", "results"];
var remove_decimals = ["fields", "from", "which", "to", "remove", "decimals"];
var filter_input_fields = [
    {element: "#id-of-the-input-control", ajax_var: "name_of_the_var_when_ajax"},
    {element: "#second-id-of-the-input-control", ajax_var: "second_name_of_the_var_when_ajax"},
];
var filter_results_div_id = "result-div";
var filter_result_item_template_id = "filtered-item-template";
var filter_result_fields = [
    {element: "data-field='name'", destination_field_id: "where to put the value when clicked"},
];
$( document ).ready(function() {
    no_results();
    setup_timer_events();
    setup_filtered_results_events();
})
function get_result_list() {
    return $(`#${filter_results_div_id}`);
}
function no_results() {
    // TODO: Need classes to disable the link without it being a dropdown menu.
    let result_list = get_result_list();
    result_list.empty();
    result_list.append($("<tr><a class='filtered-result-top disabled'><td colspan='0'>No results</td></a></tr>"));
}
function new_item(data) {
    let item_clone = $(`#${filter_result_item_template_id}`).clone();
    item_clone.attr('id', null);
    item_clone.attr("data-id", data['id']);
    item_clone.find('[data-field]').each(function() {
        let e = $(this);
        let key = e.data('field');
        if (key === undefined){
            // The template should have names on each div so this is an error.  Probably shouldn't hide it.
            return true;
        }
        if (filter_fields.includes(key)) {
            // this is a field which should show up on the page.
            let record_value = data[key];
            if (remove_decimals.includes(key)) {
                // The data from the server includes decimal places when not needed.  This seems to work to only show
                // decimal places when needed.
                // It does cut the decimals to 2, though.
                record_value = Math.round(record_value * 100) / 100;
            }
            if (is_date_value(record_value) && is_date_field(key)){
                e.text(format_date_str(record_value));
            } else {
                e.text(record_value);
            }
        } else {
            e.text("");
        }
    });
    item_clone.removeClass("hidden");
    return item_clone;
}
function get_values_to_send() {
    let values_to_send = {
        empty: true,
        "filter_fields": []
    };
    filter_input_fields.forEach(tag => {
        values_to_send[tag['ajax_var']] = $(tag['element']).val().trim();
        values_to_send["filter_fields"].push(tag['ajax_var']);
        if (values_to_send[tag['ajax_var']] !== "") {
            values_to_send['empty'] = false;
        }
    });
    return values_to_send;
}
function filtered_results_received(data) {
    let d_result_list = get_result_list();
    d_result_list.empty();
    let count = 0;
    $.each(data, function(index){
        d_result_list.append(new_item(this));
        count++;
    });
    if (count === 0) {
        no_results();
    }
    logit(`Got ${count} results.`, true);
}
function get_filtered_item_field(p, field) {
    return p.find(`[${field}]`);
}
function setup_filtered_results_events() {
    let result_list_obj = get_result_list();
    result_list_obj.on('click', '.filtered-item-link', filtered_item_click)
}
function filtered_item_click() {
    let p = $(this);
    filter_result_fields.forEach(tag => {
        let item_data_attr = tag['element'];
        let dest_tag_id = tag['destination_field_id'];
        let item_tag = get_filtered_item_field(p, item_data_attr);
        let item_val = item_tag.text().trim();
        $(`#${dest_tag_id}`).val(item_val);
    });
}

var keypress_timer;
function start_timer() {
    // logit("Starting timer...");
    window.clearTimeout(keypress_timer);
    keypress_timer = setTimeout(timer_elapsed_func, 750);
}
function timer_elapsed_func() {
    // logit("timer_elapsed_func()");
    let values_to_send = get_values_to_send();
    if (values_to_send['empty']) {
        // don't want to send empty requests.
        no_results();
        return;
    }
    var jqxhr = $.ajax({
        url: filter_url,
        type: "get",
        data: values_to_send,
        // traditional: true
    })
    .done(filtered_results_received)
    .fail(function() {
        logit("ajax fail");
    })
    .always(function() {

    });
}
function setup_timer_events() {
    filter_input_fields.forEach(tag => {
        let tag_obj = $(tag['element']);
        tag_obj.on("keydown", filter_keydown);
        tag_obj.on("focusout", input_focusout);
    });
}
function input_focusout() {
    // logit(" > clear timer from focusout");
    window.clearTimeout(keypress_timer);
}
function key_is_visible(e) {
    let donot_ignore = [
        "Backspace", "Space", "Backquote", "Equal", "Minus", "Backslash", "BracketRight", "BracketLeft", "Quote",
        "Semicolon", "Slash", "Period", "Comma",
        "KeyA", "KeyB", "KeyC", "KeyD", "KeyE", "KeyF", "KeyG", "KeyH", "KeyI", "KeyJ", "KeyK", "KeyL", "KeyM",
        "KeyN", "KeyO", "KeyP", "KeyQ", "KeyR", "KeyS", "KeyT", "KeyU", "KeyV", "KeyW", "KeyX", "KeyY", "KeyZ",
        "Digit1", "Digit2", "Digit3", "Digit4", "Digit5", "Digit6", "Digit7", "Digit8", "Digit9", "Digit0",
    ]
    return donot_ignore.includes(e.code);
}
function key_is_not_visible(e) {
    let ignore = [
        'ShiftLeft', 'MetaLeft', 'AltLeft', 'ControlLeft',
        'ShiftRight', 'MetaRight', 'AltRight', 'ControlRight',
        'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
        'Enter', 'Tab', 'CapsLock',
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"
    ]
    return ignore.includes(e.code);
}
function filter_keydown(e) {
    if (key_is_visible(e)){
        // logit(` > start timer from keydown[${e.code}]`);
        start_timer();
        return;
    }
    if (!key_is_not_visible(e)) {
        // logit(` > start timer from keydown[${e.code}]`);
        start_timer();
        return;
    }
    // logit(` > not starting timer from keydown[${e.code}]`)
}