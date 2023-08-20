// To use resize_content on a page, add the following.  "inventory-list" is the id of the div surrounding the content.
// <script type="text/javascript">
// $( document ).ready(function() {
//     let w = $(window);
//     let d = $(document);
//     w.on("resize", {"content_id": "inventory-list"}, resize_content);
//     d.on("resize", {"content_id": "inventory-list"}, resize_content);
//     w.trigger("resize");
// });
// </script>

function resize_content(e) {
    let w = $(window);
    let window_height = w.height();
    let content_obj = $(`#${e.data.content_id}`);
    let content_offset = content_obj.offset().top - w.scrollTop();
    content_obj.css("max-height", window_height - content_offset);
}

function get_screen_info() {
    let w = $(window);
    let window_height = w.height();
    let window_width = w.width();
    return {
        'window_height': window_height,
        'window_center_height': window_height / 2,
        'window_width': window_width,
        'window_center_width': window_width / 2,
    }
}