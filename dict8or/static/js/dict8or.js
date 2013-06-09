(function($) {
    'use strict';

    $(document).ready(function() {
        var packageSearchCache = {};

        $('#search-package').typeahead({
            minLength: 3,
            source: _.debounce(function(query, process) {
                if (packageSearchCache[query]) {
                    process(packageSearchCache[query]);
                    return;
                }
                $.ajax({
                    type: 'GET',
                    url: URLS.search_pypi_packages,
                    cache: false,
                    data: {
                        search: query
                    },
                    success: function(response) {
                        packageSearchCache[query] = response.packages;
                        process(response.packages);
                    }
                });
            }, 250)
        }).on('keydown', function(e) {
            var $this = $(this);
            if (e.which != 13) {
                return;
            }
            var typeahead = $this.data('typeahead');
            if (typeahead && typeahead.shown) {
                return;
            }

            $this.prop('disabled', true);
            $.ajax({
                type: 'POST',
                url: URLS.enqueue_pypi_package,
                data: {
                    'package': $this.val()
                },
                success: function(response) {
                    $this.val('');
                    if (!response.success) {
                        alert('Could not enqueue package: ' + response.msg);
                    }
                    else {
                        alert('Package successfully enqueued!');
                    }
                },
                complete: function() {
                    $this.prop('disabled', false);
                }
            });
        });
    });
})(jQuery);