// #result-list == parent element to contain the filtered results

var filter_url = "set from page as it likely uses django template tags.";
var filter_fields = ["list", "of", "fields", "to", "include", "in", "filtered", "results"];
var remove_decimals = ["fields", "from", "which", "to", "remove", "decimals"];
var filter_input_fields = [
    {element: "#id-of-the-input-control", ajax_var: "name_of_the_var_when_ajax"},
    {element: "#second-id-of-the-input-control", ajax_var: "second_name_of_the_var_when_ajax"},
];
var filter_input_empty_if_only = [];
var filter_results_div_id = "result-div";
var filter_result_item_template_id = "filtered-item-template";
var filter_hidden_data = [
    {
        "src_field": "field from result object",
        "dest_tag": "tag selector from within the template",
        "dest_attr": "attr name within that tag"},
]
var filter_result_fields = [
    {element: "data-field='name'", destination_field_id: "where to put the value when clicked"},
];
const item_selected_event_name = 'item_selected';
const filter_requested_event_name = 'filter_requested';
const filter_results_populated_event_name = 'filtered_results_populated';
const force_filter_refresh_event_name = 'force_filter_refresh';

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
    filter_hidden_data.forEach(tag => {
        console.log(`dest_tag=${tag['dest_tag']} dest_attr=${tag['dest_attr']}, src_field=${tag['src_field']}, val=${data[tag['src_field']]}`)
        let dest_tag = item_clone.find(tag['dest_tag']);
        dest_tag.attr(tag['dest_attr'], data[tag['src_field']]);
    });
    return item_clone;
}
function get_values_to_send() {
    let values_to_send = {
        empty: true,
        "wide_filter_fields": []
    };
    filter_input_fields.forEach(tag => {
        let tag_obj = $(tag['element']);
        if (tag_obj.length === 1) {
            values_to_send[tag['ajax_var']] = tag_obj.val().trim();
            values_to_send["wide_filter_fields"].push(tag['ajax_var']);
            if (values_to_send[tag['ajax_var']] !== "") {
                values_to_send['empty'] = false;
            }
        } else if (tag_obj.length > 1) {
            $.each(tag_obj, function(index) {
                let obj = $(this);
                if (obj.is("input[type='checkbox']")) {
                    if (!(tag['ajax_var'] in values_to_send)) {
                        values_to_send[tag['ajax_var']] = [];
                    }
                    if (obj.is(":checked")) {
                        values_to_send[tag['ajax_var']].push(obj.val().trim());
                    }
                } else {
                    values_to_send[tag['ajax_var']] = obj.val().trim();
                }

                if (!values_to_send["wide_filter_fields"].includes(tag['ajax_var'])) {
                    values_to_send["wide_filter_fields"].push(tag['ajax_var']);
                }
                if (!filter_input_empty_if_only.includes(tag['ajax_var'])){
                    if ((typeof(values_to_send[tag['ajax_var']]) === typeof("string")) && (values_to_send[tag['ajax_var']] !== "")) {
                        values_to_send['empty'] = false;
                    } else if ((typeof(values_to_send[tag['ajax_var']]) === typeof(['an', 'array'])) && (values_to_send[tag['ajax_var']].length !== 0)) {
                        values_to_send['empty'] = false;
                    }
                }
            });
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
    logit(`Got ${count} results.`, true);
    if (count === 0) {
        no_results();
    } else {
        $(window).trigger(filter_results_populated_event_name);
    }
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
        let dest_tag = $(`#${dest_tag_id}`);
        if (dest_tag.is("input")) {
            dest_tag.val(item_val);
        } else {
            dest_tag.text(item_val);
        }
    });
    $(window).trigger(item_selected_event_name);
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
        logit(`Got 0 results - no filter specified.`, true);
        no_results();
        $(window).trigger(filter_requested_event_name);
        return;
    }
    $(window).trigger(filter_requested_event_name);
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
        if (tag_obj.is('input[type="text"]')) {
            tag_obj.on("keydown", filter_keydown);
            tag_obj.on("focusout", input_focusout);
        }
        if (tag_obj.is('input[type="checkbox"]')) {
            tag_obj.on("click", start_timer);
        }
    });
    $(window).on(force_filter_refresh_event_name, timer_elapsed_func);
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