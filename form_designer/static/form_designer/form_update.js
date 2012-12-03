// Our class will live in the yourlabs global namespace.
if (window.yourlabs == undefined) window.yourlabs = {};

if (window.yourlabs.FormUpdate != undefined) console.log('form_update.js already loaded');

// Make jquery behave according to standards, which are compatible
// with django, else it would use PHP's implementration.
$.ajaxSettings.traditional = true;

// Little helper to make an object out of form values.
$.fn.serializeObject = function() {
    var array = $(this).serializeArray();
    var object = {};

    for (var i=0; i<array.length; i++) {
        object[array[i].name] = array[i].value;
    }

    return object;
}


window.yourlabs.FormUpdate = function(options) {
    this.form = [];
    this.modal = $('#field-configuration');
    this.modalForm = this.modal.find('.form');
    this.options = options;

    var formUpdate = this;

    this.init = function() {
        $('.form-tabs li').each(function() {
            $(this).data('form-tab', {
                verbose_name: $(this).find('.name').html(),
                pk: $(this).data('pk'),
            });
        });
        
        $('.form-tabs li:first a').click();
    };

    this.bind = function() {
        $(document).keyup(function(e) {
            if (e.which == 27) { // esc
                $('.modal .close').click();
            }
        });

        $('.modal form').live('submit', function(e) {
            e.preventDefault();
            $(this).parents('.modal').find('.save').click();
        });

        $('.modal .cancel').live('click', function() {
            $(this).parents('.modal').find('.close').click();
        });

        // {{{ widgets
        $('.field .add').click(function(e) {
            e.stopPropagation();

            var url = formUpdate.options.widgetCreateUrl;
            url += '?';
            url += $.param({
                widget_class: $(this).parents('.field').data('widget-class'),
                tab_id: $('.form-tabs .active').data('form-tab').pk,
            });
            
            $('#field-configuration').data('action', url);

            $.ajax(url, {
                type: 'get',
                async: false,
                dataType: 'html',
                success: function(data, textStatus, jqXHR) {
                    $('#field-configuration form').html(data);
                    $('#field-configuration').modal('show');
                    $('#field-configuration input:first').focus();
                },
            });
        });

        updateField = function(pk, formData) { // {{{
            var field = $('tr[data-pk=' + pk + ']');
            field.find('.verbose-name').html(formData.verbose_name);
            field.find('.help-text').html(formData.help_text);
            field.find('input[type=checkbox]').attr('checked', formData.required != undefined);
        } 
        // }}}

        createField = function(pk, formData) { // {{{ create field boilerplate
            var field = $('<tr>', {
                'data-pk': pk,
                'class': 'field',
            })

            field.append($('<td>', {
                'class': 'handle',
                html: $('<span>', {
                    'class': 'handle',
                    html: 'handle',
                }),
            }));

            $('<td>', {
                'class': 'required',
                html: $('<input>', {
                    'type': 'checkbox',
                    'checked': formData.required != undefined,
                    'disabled': 'disabled',
                }),
            }).appendTo(field);

            $('<td>', {
                'class': 'remove',
                html: '<span class="delete">delete</span>',
            }).appendTo(field);

            $('<td>', {
                'class': 'verbose-name',
                html: formData.verbose_name,
            }).appendTo(field);

            $('<td>', {
                'class': 'help',
                html: '<span class="help">help</span>',
            }).appendTo(field);

            $('<td>', {
                'class': 'help-text',
                html: formData.help_text,
            }).appendTo(field);

            $('<td>', {
                'class': 'configuration',
                html: '<span class="configuration">configuration</span>',
            }).appendTo(field);

            return field;
        } // }}}

        $('#field-configuration .save').click(function() {
            var formData = $('#field-configuration form').serializeObject();

            $.ajax($('#field-configuration').data('action'), {
                type: 'post',
                data: $('#field-configuration form').serialize(),
                success: function(data, textStatus, jqXHR) {
                    if (jqXHR.status != 201 && jqXHR.status != 204) {
                        $('#field-configuration form').html(data);
                        return;
                    }

                    $('#field-configuration').modal('hide');

                    if (jqXHR.status == 201) { // created
                        field = createField(data, formData);
                        $('.tab-pane.active table').append(field);
                    } else if (jqXHR.status == 204) { // edited
                        updateField($('#field-configuration').data(
                            'field-pk'), formData);
                        $('#field-configuration').data('field-pk', '');
                    }
                },
            });
        });

        $('.field .configuration').live('click', function() {
            var pk = $(this).parents('tr').attr('data-pk');

            var url = formUpdate.options.widgetUpdateUrl;
            url += '?';
            url += $.param({
                pk: pk,
                widget_class: $(this).parents('.field').data('widget-class'),
            });
 
            $('#field-configuration').data('action', url);
            $('#field-configuration').data('field-pk', pk);

            $.ajax(url, {
                type: 'get',
                async: false,
                dataType: 'html',
                success: function(data, textStatus, jqXHR) {
                    $('#field-configuration form').html(data);
                    $('#field-configuration').modal('show');
                },
            });
        });

        $('.field .remove').live('click', function() {
            var row = $(this).parents('tr');

            $('#delete-field').data('field-pk', row.attr('data-pk'));
            $('#delete-field .field-name').html( 
                row.find('.verbose-name').html());
            $('#delete-field').modal('show');
        });

        $('#delete-field .save').bind('click', function() {
            var pk = $('#delete-field').data('field-pk');

            $.ajax(formUpdate.options.widgetDeleteUrl, {
                async: false,
                type: 'post',
                data: {'pk': pk},
                success: function() {
                    $('tr[data-pk=' + pk + ']').remove();
                    $('#delete-field').modal('hide');
                },
            });
        });

        $('table').sortable({
            axis: 'y',
            handle: '.handle',
            items: '.field',
            stop: function(e, ui) {
                var pks=[];
                $(e.target).find('.field').each(function() {
                    pks.push($(this).attr('data-pk'));
                });
                $.post(formUpdate.options.formUpdateUrl, {
                    pk: $('.form-tabs li.active').data('pk'), widgets: pks});
            },
        });
        // }}}

        // {{{ tabs
        $('.new-tab').click(function() {
            $('#new-tab').modal('show');
            $('#new-tab input[type=text]:first').focus();
        });

        $('#new-tab .save').click(function() {
            var verboseName = $('#new-tab input[name=verbose_name]').val();

            if (! $.trim(verboseName).length) {
                $('#new-tab .control-group').addClass('error');

                $('<span>', {
                    'class': 'help-inline',
                    html: gettext('Please type the tab title'),
                }).insertAfter('#new-tab input[name=verbose_name]');
                
                return;
            }

            $.ajax(formUpdate.options.tabCreateUrl, {
                async: false,
                type: 'post',
                data: {
                    verbose_name: verboseName,
                    form_pk: $('#form-pk').val(),
                },
                dataType: 'json',
                success: function(data, textStatus, jqXHR) {
                    var id = data.tab.pk;

                    $('<div>', {
                        id: 'tab-' + id,
                        'class': 'tab-pane',
                        html: $('<table>', {
                            'class': 'fieldset',
                        }),
                    }).insertAfter('.tab-list div:last');
        
                    var tab = $('<li>', {
                        html: $('<a>', {
                            href: '#tab-' + id,
                            'data-toggle': 'tab',
                            html: [
                                '<span class="handle">handle</span>',
                                '<span contenteditable="true" class="name">',
                                data.tab.verbose_name,
                                '</span>',
                                '<span class="remove">remove</span>',
                            ].join(''),
                        })
                    });
                    tab.data('form-tab', data.tab);
                    tab.insertBefore($('li.new-tab'));

                    $('#new-tab').modal('hide');
                    $('#new-tab input[type=text]').val('');
                    $('#new-tab .help-inline').remove();
                    $('#new-tab .error').removeClass('error');

                    $('.form-tabs li:not(.new-tab):last a').click();
                },
            });
        });

        $('.form-tabs .remove').live('click', function() {
            var data = $(this).parents('li').data('form-tab');
            $('#delete-tab .tab-name').html(data.verbose_name);
            $('#delete-tab').data('tab-pk', data.pk);
            $('#delete-tab').modal('show');
        });

        $('#delete-tab .save').bind('click', function() {
            var data = $('a[href=#tab-'+$('#delete-tab').data('tab-pk')+']').parents('li'
                ).data('form-tab');

            $.ajax(formUpdate.options.tabDeleteUrl, {
                async: false,
                type: 'post',
                data: data,
                success: function() {
                    $('div#tab-' + data.pk).remove();
                    $('a[href=#tab-' + data.pk + ']').remove();
                    $('#delete-tab').modal('hide');
                },
            });
        });

        $('.form-tabs .name').live('focusout', function() {
            var data = $(this).parents('li').data('form-tab');
            $.post(formUpdate.options.tabUpdateUrl, {
                pk: data.pk,
                name: $(this).html(),
            });
        });

        $('.form-tabs').sortable({
            axis: 'x',
            handle: '.handle',
            items: 'li:not(.new-tab)',
            stop: function(e, ui) {
                var pks=[];
                $('.form-tabs li:not(.new-tab)').each(function() {
                    pks.push($(this).data('form-tab').pk);
                });
                $.post(formUpdate.options.formUpdateUrl, {tabs: pks});
            },
        });

        // }}}
    };

    this.currentTabContent = function() {
        return $('.tab-pane.active');
    };

    this.fieldFormUrl = function(widget_class) {
    }

    this.createFieldHtml = function(configuration) {
        $('<tr>', {
            'class': 'field',
            html: [
                $('<td>'),
            ].join(''),
        });
    };

    this.showFieldConfiguration = function(field) {
        var data = typeof(field) == 'string' ? {} : field.data('configuration');
        
        this.modalForm.data('field', field);

        $.ajax(this.fieldUrl(widget_class), {
            async: false,
            data: data,
            type: 'post',
            dataType: 'html',
            success: function(data, jqXHR, textStatus) {
                formUpdate.modalForm.html(data);
            },
        });
    };

    this.sendForm = function() {
        $.ajax(this.fieldUrl(this.modalForm.data('widget_class')), {
            async: false,
            data: formUpdate.modalForm.serialize(),
            type: 'post',
            dataType: 'json',
            success: function(data, jqXHR, textStatus) {
                if (data.is_valid) {
                    var html = this.createFieldHtml(data.field);
                    var table = formUpdate.currentTabContent().find('table');

                    if (typeof(formUpdate.modalForm.data('field')) == 'string') {
                        table.append(html);
                    } else {
                        var current = table.find('tr#field-' + data.field.pk)
                        current.html(html.html());
                    }
                } else {
                    formUpdate.modalForm.html(data);
                }
            },
        });
    }
}
