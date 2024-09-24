// TODO: cache responses?  seems fast at the moment.  Put cache on a later list.
var autocomplete_keypress_timer;
var autocomplete_url = "set from page as it likely uses django template tags.";
var autocomplete_fields = ["list", "of", "fields", "to", "include", "in", "dropdown"];
var autocomplete_display_field = "name of the field to use when clicking on a dropdown item";
var autocomplete_copy_values = {}; // dict of autocomplete_column:form_field pairs to copy when an item is selected.
var autocomplete_li_template_id = "id of li to use as a template";
var autocomplete_remove_decimal_fields = []
var autocomplete_container_id = "line_item_list";
var autocomplete_debug_log = false;  // set to true to get a lot of logging.
var autocomplete_extra_data_func = "Set to a function which returns some extra data for the autocomplete to pass on to the server.";
var autocomplete_focus_after_select = "id of field to focus on after selecting autocomplete dropdown item";

$( document ).ready(function() {
    // TODO: Why can't this call autocomplete_setup_events()?  Did I not try it?  Or does it need to be done after the
    //  main page sets the above globals?
    ac_no_results();
})
function ac_logit(value) {
    if (autocomplete_debug_log) {
        logit(value);
    }
}
function ac_start_timer(caller) {
    window.clearTimeout(autocomplete_keypress_timer);
    autocomplete_keypress_timer = setTimeout(ac_timer_elapsed_func, 750, caller);
}
function ac_no_results() {
    $(".dropdown-menu").each(function() {
        $(this).empty();
        $(this).append($("<li><a class='dropdown-item disabled'>No results</a></li>"));
    });
}
function ac_new_dropdown_item(data) {
    var ac_li_template = $(`#${autocomplete_li_template_id}`);
    console.log(ac_li_template);
    var new_ac_li = ac_li_template.clone();
    new_ac_li.attr('id', null);
    $(new_ac_li.find('a')).attr("data-id", data['id']);
    new_ac_li.find('div').each(function() {
        var e = $(this);
        var key = e.attr('name');
        if (key === undefined){
            return true;
        }
        if (autocomplete_fields.includes(key)) {
            let v = data[key];
            if (autocomplete_remove_decimal_fields.includes(key)) {
                // The data from the server includes decimal places when not needed.  This seems to work to only show
                // decimal places when needed.
                v = Math.round(v * 100) / 100;
            }
            // TODO: need to get date_str.js into scrap and the media class.
            if (is_date_value(v) && is_date_field(key)){
                e.text(format_date_str(v));
            } else {
                e.text(v);
            }
        }
    });
    new_ac_li.removeClass("hidden");
    return new_ac_li;
}
function ac_timer_elapsed_func(caller_obj) {
    var caller = $(caller_obj);
    var t = ac_get_dropdown_textbox(caller);
    var text_value = t.val().trim();

    if (text_value === "") {
        // don't want to send empty requests.
        ac_no_results();
        return;
    }
    let data_to_send = {
        terms: text_value,
        field: "cryptic_name",
    };
    if (autocomplete_extra_data_func instanceof Function) {
        data_to_send['extra'] = JSON.stringify(autocomplete_extra_data_func());
    }
    ac_logit(`timer: ${t.prop('id')} send &quot;${text_value}&quot; to ${autocomplete_url}`);
    console.log(data_to_send);
    var jqxhr = $.ajax({
        url: autocomplete_url,
        type: "get",
        data: data_to_send,
        caller_id: caller.prop('id'),
        terms: text_value
    })
    .done(function(data) {
        var d_caller = $(document.getElementById(this.caller_id));
        console.log(d_caller);
        var d_ddl = ac_get_dropdown_list(d_caller)
        d_ddl.empty();
        var count = 0;
        $.each(data, function(index){
            d_ddl.append(ac_new_dropdown_item(this));
            count++;
        });
        if (count === 0) {
            ac_no_results();
        }
        ac_logit(`Got ${count} results for "${this.terms}".`)
        if (d_caller.find('.dropdown-menu').is(":hidden")){
            // logit("dropdown is hidden, toggling dropdown");
            // TODO: toggle doesn't work.
            d_caller.dropdown('toggle');
        } else {
            // ac_logit("NOT toggling dropdown");
        }
    })
    .fail(function() {
        ac_logit("ajax fail");
    })
    .always(function() {
        // ac_logit("ajax complete");
    });
}
function ac_get_dropdown_parent(e) {
    // confirmed used when typing into text box ////////////////////////////////////////////////////////////////
    // Given any element within a dropdown tree, return the top-most element.
    let e_jq = $(e);
    let ret = e_jq.parents(".dropdown");
    // measure_form.html
    // ac_get_dropdown_parent(undefined) = id_item-dropdown, field_name = item
    // sourceitem_create.html
    // ac_get_dropdown_parent(undefined) = id_lineitemform-0-source_category-dropdown, field_name = source_category
    ac_logit(`ac_get_dropdown_parent(${e_jq.attr('id')}) = ${ret.attr('id')}, field_name = ${ret.attr('data-field-name')}`);
    // ret = id_lineitemform-0-cryptic_name-dropdown
    return ret;
}
function ac_get_dropdown_div(p) {
    return p.children(".dropdown");
}
function ac_get_dropdown_textbox(p) {
    // confirmed used when typing into text box ////////////////////////////////////////////////////////////////
    // measure_form.html
    // ac_get_dropdown_textbox(id_item-dropdown) = id_item-text
    // sourceitem_create.html
    // ac_get_dropdown_textbox(id_lineitemform-0-source_category-dropdown) = id_lineitemform-0-source_category-text
    let ret = p.children("input[type='text']");
    ac_logit(`ac_get_dropdown_textbox(${p.attr('id')}) = ${ret.attr('id')}`);
    return ret;
}
function ac_get_dropdown_list(p) {
    // confirmed used when typing into text box ////////////////////////////////////////////////////////////////
    let ret = p.children(".dropdown-menu");
    ac_logit(`ac_get_dropdown_list(${p.attr('id')}) = ${ret.attr('id')}`);
    return ret;
}
function ac_get_hidden_model_field(p) {
    // measure_form.html
    // ac_get_hidden_model_field([object Object]) = item
    // sourceitem_create.html
    // ac_get_hidden_model_field([object Object]) = lineitemform-0-source_category
    let id_text = p.prop("id");
    id_text = id_text.substring(0, id_text.length - "-dropdown".length);
    let ret = $(document.getElementById(id_text));
    ac_logit(`ac_get_hidden_model_field(${p}) = ${ret.attr('name')}`);
    return ret;
}
function ac_get_autocomplete_field(e, field_name) {
    // measure_form.html
    // !!! ac_get_autocomplete_field(undefined, id) = undefined
    // sourceitem_create.html
    // ac_get_autocomplete_field(undefined, cryptic_name) = cryptic_name
    // ac_get_autocomplete_field(undefined, source_category) = source_category
    let ret = e.find(`div[name="${field_name}"]`);
    ac_logit(`ac_get_autocomplete_field(${e.attr('id')}, ${field_name}) = ${ret.attr('name')}`);
    return ret;
}
function ac_get_form_field_name(p){
    // measure_form.html
    // ac_get_form_field_name(id_item-dropdown) = item
    // sourceitem_create.html
    // ac_get_form_field_name(id_lineitemform-0-source_category-dropdown) = source_category
    // Given "id_lineitemform-0-cryptic_name-dropdown"
    // Return the data-field-name from tag.
    let ret = p.attr("data-field-name");
    ac_logit(`ac_get_form_field_name(${p.attr('id')}) = ${ret}`);
    return ret;
}
function ac_get_form_prefix(p) {
    // measure_form.html
    // ac_get_form_prefix(id_item-dropdown) - 'id_item-dropdown' =
    // sourceitem_create.html
    // ac_get_form_prefix(id_lineitemform-0-source_category-dropdown) - 'source_category-dropdown' = id_lineitemform-0-
    let id_text = p.prop("id");
    let remove_this = `${ac_get_form_field_name(p)}-dropdown`;
    if (!ac_is_formset()) {
        remove_this = id_text;
    }
    let ret = id_text.substring(0, id_text.length - remove_this.length);
    ac_logit(`ac_get_form_prefix(${p.attr('id')}) - '${remove_this}' = ${ret}`);
    return ret;
}
function ac_get_form_field(p, form_prefix, form_field) {
    // measure_form.html
    // ac_get_form_field(id_item-dropdown, , id_item-text) = id_item-text
    // <input type="hidden" name="item" placeholder="Pick an item" required="" id="id_item" value="nope">
    // sourceitem_create.html
    // ac_get_form_field(id_lineitemform-0-source_category-dropdown, id_lineitemform-0-, source_category) = id_lineitemform-0-source_category
    // <input type="hidden" name="lineitemform-0-source_category" placeholder="category from source" id="id_lineitemform-0-source_category" value="nope">
    // return $(document.getElementById(`${form_prefix}${form_field}`));
    if (!ac_is_formset()) {
        form_prefix = "";
    }
    let ret = $(`#${form_prefix}${form_field}`);
    ac_logit(`ac_get_form_field(${p.attr('id')}, ${form_prefix}, ${form_field}) = ${ret.attr('id')}`);
    return ret;
}
function ac_is_formset(){
    return ($(`#${autocomplete_container_id}`).find(".empty-form").length !== 0);
}
function autocomplete_setup_events() {
    let autocomplete_container = $(`#${autocomplete_container_id}`);
    autocomplete_container.on("click", "button", function(e) {
        ac_logit("Log of jquery events.", true);
    });
    autocomplete_container.on("keypress", "input", function(e) {
        ac_start_timer(ac_get_dropdown_parent(this));
    })
    autocomplete_container.on("keydown", "input", function(e) {
        switch (e.keyCode) {
            case 8: // Backspace
                ac_start_timer(ac_get_dropdown_parent(this));
                break;
            case 9: // Tab
            case 13: // Enter
            case 37: // Left
            case 38: // Up
            case 39: // Right
            case 40: // Down
                break;
            default:
                break;
        }
    });
    autocomplete_container.on("focusout", "input", function() {
        window.clearTimeout(autocomplete_keypress_timer);
    })
    autocomplete_container.on('click', 'a.dropdown-item', function() {
        let e = $(this);
        let p = ac_get_dropdown_parent(e);
        let selected_item = "";
        let n = "nope";
        if (autocomplete_display_field !== "") {
            n = ac_get_autocomplete_field(e, autocomplete_display_field);
            selected_item = n.text();
        }
        let t = ac_get_dropdown_textbox(p);
        let h = ac_get_hidden_model_field(p);
        let form_prefix = ac_get_form_prefix(p);

        for (const [key, value] of Object.entries(autocomplete_copy_values)) {
            let copy_field = ac_get_autocomplete_field(e, key);
            let form_field = ac_get_form_field(p, form_prefix, value);
            if (form_field.parent().hasClass('with-autocomplete')) {
                // This is because the autocomplete fields have an input for display purposes and a hidden input for
                // saving.  The display input is the same id as the hidden but with "-text" added.
                let subform_field = $(`#${form_field.attr('id')}-text`)
                ac_logit(`Changing autocomplete field ${subform_field.attr('id')} from "${subform_field.text()}" to "${copy_field.text()}"`)
                subform_field.val(copy_field.text());
            }
            ac_logit(`Changing ${form_field.attr('id')} from "${form_field.text()}" to "${copy_field.text()}"`)
            form_field.val(copy_field.text());
        }
        // ac_logit(`clicked dropdown item: &quot;${selected_item}&quot; ${e.data("id")} and setting ${t.prop("id")} AND ${h.prop("id")}`);
        // if (n !== "nope") {
        //     t.val(n.text());
        // }
        h.val(e.data("id"));
        // $("#jquery-example-2-text").val(n.text());
        if (!autocomplete_focus_after_select.includes(" ")) {
            ac_get_form_field(p, form_prefix, autocomplete_focus_after_select).focus();
        }
    })
    autocomplete_container.on('show.bs.dropdown', 'div.dropdown', function () {
        // ac_logit("show.bs.dropdown");
    })
    autocomplete_container.on('shown.bs.dropdown', 'div.dropdown', function () {
        // ac_logit("shown.bs.dropdown");
    })
    autocomplete_container.on('hide.bs.dropdown', 'div.dropdown', function () {
        // ac_logit("hide.bs.dropdown");
    })
    autocomplete_container.on('hidden.bs.dropdown', 'div.dropdown', function () {
        // ac_logit("hidden.bs.dropdown");
    })
}
