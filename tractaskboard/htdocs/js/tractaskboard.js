// -*- coding: utf-8 -*-

$(function() {
    $('.taskboard_tickets').sortable({
        dropOnEmpty: true,
        connectWith: ['.taskboard_tickets'],
        placeholder: 'taskboard_placeholder',
        forcePlaceholderSize: true
    });

    $('.taskboard_tickets').bind('sortreceive', function(event, ui) {
        // save new status
        var elem = $(event.target);
        var form = ui.item.find('.ticket_status_form').first();
        var status = form.find('input[name="status"]').first();
        status.val(elem.prev().text());
        form.ajaxSubmit();
    });

    var ticketCount = $('.taskboard_ticket').size();
    var ticketHeight = $('.taskboard_ticket').first().outerHeight({ margin: true });
    var statusHeight = $('.taskboard_lane_status').first().outerHeight({ margin: true });

    $('.taskboard_lane').height(ticketHeight * ticketCount + statusHeight);
    $('.taskboard_tickets').height(ticketHeight * ticketCount);
});