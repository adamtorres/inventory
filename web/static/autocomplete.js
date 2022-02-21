// TODO: cache responses?  seems fast at the moment.  Put cache on a later list.
var keypress_timer;
var autocomplete_url = "set from page as it likely uses django template tags.";

$( document ).ready(function() {
    no_results();
})
function logit(stuff, clear=false) {
    if (clear) {
        $("#jquery-example-2-log").empty();
    }
    $("#jquery-example-2-log").append(stuff + "\n");
}
function start_timer(caller) {
    window.clearTimeout(keypress_timer);
    keypress_timer = setTimeout(timer_elapsed_func, 750, caller);
}
function no_results() {
    $(".dropdown-menu").each(function() {
        $(this).empty();
        $(this).append($("<li><a class='dropdown-item disabled'>No results</a></li>"));
    });
}
function new_dropdown_item(data) {
    var ddit = $("#dropdown-item-template");
    var new_ddi = ddit.clone();
    new_ddi.attr('id', null);
    $(new_ddi.find('a')).attr("data-id", data['id']);
    to_edit_attributes = ["identifier", "name", "pack_quantity", "unit_size"];
    new_ddi.find('div').each(function() {
        var e = $(this);
        var key = e.attr('name');
        if (key === undefined){
            return true;
        }
        if (to_edit_attributes.includes(key)) {
            v = data[key];
            if (key === "pack_quantity") {
                // The data from the server includes decimal places when not needed.  This seems to work to only show
                // decimal places when needed.
                v = Math.round(v * 100) / 100;
            }
            e.text(v);
        }
    });
    new_ddi.removeClass("hidden");
    return new_ddi;
}
function timer_elapsed_func(caller_obj) {
    var caller = $(caller_obj);
    var t = get_dropdown_textbox(caller);
    var text_value = t.val()

    if (text_value.length < 1) {
        // don't want to send empty requests.
        no_results();
        return;
    }
    logit(`timer: ${t.prop('id')} send &quot;${text_value}&quot; to ${autocomplete_url}`);
    var jqxhr = $.ajax({
        url: autocomplete_url,
        type: "get",
        data: {
            terms: text_value,
            sources: $( "#source" ).val()
        },
        caller_id: caller.prop('id'),
        terms: text_value
    })
    .done(function(data) {
        var d_caller = $(document.getElementById(this.caller_id));
        var d_ddl = get_dropdown_list(d_caller)
        d_ddl.empty();
        var count = 0;
        $.each(data, function(index){
            d_ddl.append(new_dropdown_item(this));
            count++;
        });
        if (count === 0) {
            no_results();
        }
        logit(`Got ${count} results for "${this.terms}".`)
        if (d_caller.find('.dropdown-menu').is(":hidden")){
            // logit("dropdown is hidden, toggling dropdown");
            // TODO: toggle doesn't work.
            d_caller.dropdown('toggle');
        } else {
            logit("NOT toggling dropdown");
        }
    })
    .fail(function() {
        logit("ajax fail");
    })
    .always(function() {
        logit("ajax complete");
    });
}
$("#item-list").on("click", "button", function(e) {
    logit("Log of jquery events.", clear=true);
});
$("#item-list").on("keypress", "input", function(e) {
    start_timer(get_dropdown_parent(this));
})
$("#item-list").on("keydown", "input", function(e) {
    switch (e.keyCode) {
        case 8: // Backspace
            start_timer(get_dropdown_parent(this));
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
$("#item-list").on("focusout", "input", function() {
    window.clearTimeout(keypress_timer);
})
function get_dropdown_parent(e) {
    // Given any element within a dropdown tree, return the top-most element.
    return $(e).parents(".dropdown");
}
function get_dropdown_div(p) {
    return p.children(".dropdown");
}
function get_dropdown_textbox(p) {
    return p.children("input[type='text']");
}
function get_dropdown_list(p) {
    return p.children(".dropdown-menu");
}
function get_hidden_model_field(p) {
    id_text = p.prop("id");
    id_text = id_text.substring(0, id_text.length - "-dropdown".length);
    return $(document.getElementById(id_text));
}
$('#item-list').on('click', 'a.dropdown-item', function() {
    // $( "div" ).data( "role" ) === "page";
    var e = $(this);
    var p = get_dropdown_parent(e);
    var n = e.find('div[name="name"]');
    var selected_item = n.text();
    var t = get_dropdown_textbox(p);
    var h = get_hidden_model_field(p);
    logit(`clicked dropdown item: &quot;${selected_item}&quot; ${e.data("id")} and setting ${t.prop("id")} AND ${h.prop("id")}`);
    t.val(n.text());
    h.val(e.data("id"));
    // $("#jquery-example-2-text").val(n.text());
})
$('#item-list').on('show.bs.dropdown', 'div.dropdown', function () {
    // logit("show.bs.dropdown");
})
$('#item-list').on('shown.bs.dropdown', 'div.dropdown', function () {
    // logit("shown.bs.dropdown");
})
$('#item-list').on('hide.bs.dropdown', 'div.dropdown', function () {
    // logit("hide.bs.dropdown");
})
$('#item-list').on('hidden.bs.dropdown', 'div.dropdown', function () {
    // logit("hidden.bs.dropdown");
})
