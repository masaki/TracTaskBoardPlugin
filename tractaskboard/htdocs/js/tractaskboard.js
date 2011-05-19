// -*- coding: utf-8 -*-

$(function() {
    var resizeLaneToMaxSize = function() {
        var ticketCount = $('.taskboard_ticket').size();
        var ticketHeight = $('.taskboard_ticket').first().outerHeight({ margin: true });
        var statusHeight = $('.taskboard_lane_status').first().outerHeight({ margin: true });

        $('.taskboard_lane').height(ticketHeight * ticketCount + statusHeight);
        $('.taskboard_tickets').height(ticketHeight * ticketCount);
    };

    $('.taskboard_tickets').sortable({
        dropOnEmpty: true,
        connectWith: ['.taskboard_tickets'],
        placeholder: 'taskboard_placeholder',
        forcePlaceholderSize: true
    });

    $('.taskboard_tickets').bind('sortover', function(event, ui) {
        //
    });

    $('.taskboard_tickets').bind('sortreceive', function(event, ui) {
        // save new status
        elem = $(event.target);
        $.post($('a.taskboard_api').first().attr('href'), {
            id: /taskboard_ticket_(\d+)/.exec(ui.item.attr("id"))[1],
            status: elem.prev().text()
        });
    });

    resizeLaneToMaxSize();
});