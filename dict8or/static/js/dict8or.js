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
            if (e.which != 13) {
                return;
            }
            var typeahead = $(this).data('typeahead');
            if (typeahead && typeahead.shown) {
                return;
            }
            console.log('Add package: ' + this.value);
        });
    });
})(jQuery);