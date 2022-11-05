let at_timers = {};
var arbitrary_timer_debug_log = false;

function at_logit(value) {
    if (arbitrary_timer_debug_log) {
        logit(value);
    }
}

function at_add_timer(timer_name, timeout, timer_elapsed_func) {
    at_logit(`at_add_timer: '${timer_name}' '${timeout}'`);
    at_timers[timer_name] = {
        'timer': null,
        'timeout': timeout,
        'timer_elapsed_func': timer_elapsed_func
    };
}

function at_start_timer(caller, timer_name) {
    window.clearTimeout(at_timers[timer_name]['timer']);
    at_timers[timer_name]['timer'] = setTimeout(
        at_timers[timer_name]['timer_elapsed_func'], at_timers[timer_name]['timeout'], caller);
}

function at_clear_timer(timer_name) {
    window.clearTimeout(at_timers[timer_name]['timer']);
}

function at_add_keypress_events(trigger_element_parent_id, timer_name) {
    // $._data(document.getElementById("id_order_number"), 'events'); shows the three events are created.
    let trigger_element_parent = $(`${trigger_element_parent_id}`);
    at_logit(`at_add_keypress_events(${trigger_element_parent_id}, ${timer_name})`);
    console.log(trigger_element_parent);
    trigger_element_parent.on("keypress", "input", function (e) {
        at_logit(`keypress: (${trigger_element_parent_id}, ${timer_name})`);
        console.log(`keypress: trigger_element_id='${trigger_element_parent_id}' timer_name='${timer_name}'`);
        at_start_timer(trigger_element_parent, timer_name);
    })
    trigger_element_parent.on("keydown", "input", function (e) {
        at_logit(`keydown: (${trigger_element_parent_id}, ${timer_name})`);
        console.log(`keydown: trigger_element_id='${trigger_element_parent_id}' timer_name='${timer_name}'`);
        switch (e.keyCode) {
            case 8: // Backspace
                at_start_timer(trigger_element_parent, timer_name);
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
    trigger_element_parent.on("focusout", "input", function (e) {
        at_logit(`focusout: (${trigger_element_parent_id}, ${timer_name})`);
        console.log(`focusout: trigger_element_id='${trigger_element_parent_id}' timer_name='${timer_name}'`);
        at_clear_timer(timer_name);
    });
}

function at_add_timer_with_events(timer_name, timeout, timer_elapsed_func, trigger_element_parent_id) {
    at_add_timer(timer_name, timeout, timer_elapsed_func);
    at_add_keypress_events(trigger_element_parent_id, timer_name);
}