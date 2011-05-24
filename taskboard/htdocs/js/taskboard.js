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
        var ticketHolder = $(event.target);
        var thisTicket   = ui.item;

        var ticketId = /taskboard_ticket_(\d+)/.exec(thisTicket.attr('id'))[1];
        var newState = ticketHolder.prev('h2.taskboard_lane_status').text();

        $.post(
            $('#taskboard_api').val(),
            {
                id: ticketId,
                status: newState,
                __FORM_TOKEN: $('#taskboard_form_token').val()
            },
            function(res) {
                $.ajax({
                    url: $('#taskboard_rpc').val(),
                    type: 'post',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        method: 'ticket.update',
                        params: [
                            ticketId,
                            "update from TracTaskBoardPlugin using JSON-RPC",
                            { action: res['action'], status: newState },
                        ]
                    }),
                    dataType: 'json',
                    success: function(data) {
                        console.log(data);
                    }
                });
            },
            'json'
        );
    });

    var ticketCount = $('.taskboard_ticket').size();
    var ticketHeight = $('.taskboard_ticket').first().outerHeight({ margin: true });
    var statusHeight = $('.taskboard_lane_status').first().outerHeight({ margin: true });

    $('.taskboard_lane').height(ticketHeight * ticketCount + statusHeight);
    $('.taskboard_tickets').height(ticketHeight * ticketCount);
});