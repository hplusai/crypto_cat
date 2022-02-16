/**
  * Simple jQuery utility for saving element values in localStorage.
  *
  * Usage: 
  *  - Add class "store" to the element you want to save.
  *  - Add id attribute to the element or specify your own storage key (attribute data-storage-name)
  *  - Add attribute "data-storage-name" to the element if you 
  *        want to control under which name the value will be stored
  *  - Add attribute "data-storage-noload" to suppress loading (will be stored though, it is 
  *        useful, when HTML-specified value is temporarily more important).
  *
  * The utility tries to be jQuery Mobile aware but it is not complete.
  *
  * (c) Jan Pipek 2013 - jan.pipek@gmail.com
  */
var upars = new URLSearchParams(location.search);
var uniq_key=upars.toString();
//(function($) {
    var InputStorage = {
        /**
         * Check if the browser supports storage.
         */
        storageEnabled : typeof(Storage) !== "undefined",

        getElementStorageKey : function($element) {
            if ($element.data("storage-name")) {
                return "elements-" + $element.data("storage-name");
            } else if ($element.attr("id")) {
                return "elements-id-" + $element.attr("id");
            }
            return null;
        },

        getElementValue : function($element) {
            // $element - single element!
            if ($element.is(":radio, :checkbox")) {
                return $element.is(":checked") ? "true" : "false";
            }
            else if ($element.is("input, textarea, select")) {
                return $element.val();
            }
        },

        storeElementState : function($element) {
            // $element - single element!
            if (!this.storageEnabled) return;
            var key = this.getElementStorageKey($element);
            if (!key) {
                console.log("Cannot store element state:");
                console.log($element);
                return;
            }

            // Saving by different element types
            value = this.getElementValue($element);

            // console.log("saving to storage: " + key + ", value: " + value);
            window.localStorage[uniq_key+key] = value;
        },

        loadElementState : function($element) {
            // $element - single element!
            if (!this.storageEnabled) return;
            if (!$element.data("storage-noload")) {
                var key = this.getElementStorageKey($element);
                if (!key) {
                    console.log("Cannot load element state:");
                    console.log($element);
                    return;
                }
                var originValue = this.getElementValue($element);
                var value = localStorage[uniq_key+key];
                if (value && value != originValue) { 
                    // console.log("loading from storage: " + key + ", value: " + value);
                    if ($element.is(":checkbox, :radio")) {
                        if (value == "true") {
                            $element.attr("checked", true);
                        } else {
                            $element.removeAttr("checked");
                        }
                        if ($.mobile && $element.checkboxradio) {
                            // Needed for UI update in jQuery Mobile
                            $element.checkboxradio( "refresh" );
                        }
                    } else if ($element.is("input, textarea, select")) {
                        $element.val(value);
                    }
                    $element.trigger("change");
                }
            }
            $element.data("storage-loaded", true);
        }
    };

    // Force element loading
    $.fn.loadState = function() {
        $.each($(this), function() {
            InputStorage.loadElementState($(this));
        });
    };

    // Force element saving
    $.fn.saveState = function() {
        $.each($(this), function() {
            InputStorage.saveElementState($(this));
        });
    }


//    $(function() {
function load_store() {
        // Enable data storage on page load
        var $withState = $("textarea.store, select.store, input.store,.store input, .store textarea, .store select");//.filter("input, textarea, select");
        $withState.change(function() {
            if (!$(this).data("storage-loaded")) {
                // storage-loaded is set only after the loading process is finished.
                // Until then, don't respond.
                return;
            }
            InputStorage.storeElementState($(this));
            $withState.filter(":checkbox, :radio").each(function() {
                InputStorage.storeElementState($(this));
            });
        });
        $withState.each(function() {
            InputStorage.loadElementState($(this));
        });
}
//);

//) (jQuery);