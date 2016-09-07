/**
 * JS Namespacing Support
 * Added by Ray Brown <ray@bitmanic.com> as referenced here:
 * github.com/jashkenas/coffeescript/wiki/FAQ#user-content-unsupported-features
 * -----------------------------------------------------------------------------
 * Usage:
 *
 * namespace('Hello.World', function(exports) {
 *   exports.hi = function() {
 *     console.log('Hi World!');
 *   };
 * });
 *
 * namespace('Say.Hello', function(exports, top) {
 *   exports.fn = function() {
 *     top.Hello.World.hi();
 *   };
 * });
 *
 * Say.Hello.fn();
 *
 */
var __slice = [].slice;
var namespace = function(target, name, block) {

  var item, top, _i, _len, _ref, _ref1;

  if (arguments.length < 3) {
    _ref = [(typeof exports !== 'undefined' ? exports : window)].concat(__slice.call(arguments));
    target = _ref[0];
    name = _ref[1];
    block = _ref[2];
  }

  top = target;
  _ref1 = name.split('.');

  for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
    item = _ref1[_i];
    target = target[item] || (target[item] = {});
  }

  block(target, top);
};

/**
 * Execute when the document is ready
 */
jQuery(document).ready(function($){

  /**
   * AO Spin code
   */
  namespace("AO.Spin", function(exports) {

    /**
     * Toggle logo on scroll (non-mobile)
     */
    exports.LogoSwap = function(){
      $('main').waypoint(function(direction) {
        $("#ao-logo-wordmark").addClass('animated');
        $(".symbol-red").addClass('animated');
        if (direction === 'down') {
          $("#ao-logo-wordmark").addClass('fadeOutUp').removeClass('fadeInDown');
          $(".symbol-red").removeClass('fadeOutUp').addClass('fadeInDown');
        } else {
          $("#ao-logo-wordmark").removeClass('fadeOutUp').addClass('fadeInDown');
          $(".symbol-red").addClass('fadeOutUp').removeClass('fadeInDown');
        }
      });
    };

    /**
     * Nav link hover effect (non-mobile)
     */
    exports.NavHover = function(){
      $("#main-nav a").hover(
        function() {
          $(this).addClass("hover");
          $(this).find('span').addClass("animated fadeInRight");
        },
        function() {
          $(this).removeClass("hover");
        }
      );
    };

    /**
     * Generic toggling function
     * ---
     * Usage:
     * <a data-toggle="#thing-to-toggle">Click me</a>
     * <div id="thing-to-toggle">
     *   This element will gain and lose the "open" class when toggled.
     * </div>
     */
    exports.ToggleOpen = function(){
      $("[data-toggle]").on("click", function(e) {

        e.preventDefault();

        var trigger = $(this);
        var selector = trigger.data("toggle");
        var target = $(selector);
        var allTriggers = $("[data-toggle=" + selector + "]");

        if (target.hasClass("open")) {
          target.removeClass("open");
          allTriggers.removeClass("triggered");
        } else {
          target.addClass("open");
          allTriggers.addClass("triggered");
        }

      });
    };

    /**
     * Build and manage the blog post grid
     */
    exports.MasonryInit = function() {

      // The thing that holds our grid items
      var container = $('#masonry');

      // Responsive breakpoints
      var breakpoints = {
        mobile: 900,
        phone: 600
      };

      // When the window loads or is resized...
      // TODO: throttle this resize event
      $(window).on("load resize", function() {

        // Setup
        var windowWidth = $(window).width();
        var containerWidth = container.width();
        var cols;

        // Determine how many columns to show
        if (windowWidth < breakpoints.phone) {
          container.attr("data-cols", 1);
          cols = 1;
        } else if (windowWidth < breakpoints.mobile) {
          container.attr("data-cols", 2);
          cols = 2;
        } else {
          container.attr("data-cols", 3);
          cols = 3;
        }

        // Configure and initialize Masonry
        container.masonry({
          isInitLayout: false,
          itemSelector: ".masonry-item",
          columnWidth: containerWidth / cols
        });

        // Find the Masonry instance
        var msnry = container.data("masonry");

        // Add an attribute to the container when layout is complete (for styling)
        msnry.on( 'layoutComplete', function() {
          container.attr("data-layout", "complete");
        });

        // Trigger Masonry layout
        msnry.layout();

      });

    };

    /**
     * Fix some sort of visual bug that occurs when the "skip" link is focused
     * (I don't know, I just pulled this undocumented code into this file.)
     */
    exports.SkipLinkFocusFix = function() {

      var is_webkit = navigator.userAgent.toLowerCase().indexOf( 'webkit' ) > -1,
          is_opera  = navigator.userAgent.toLowerCase().indexOf( 'opera' )  > -1,
          is_ie     = navigator.userAgent.toLowerCase().indexOf( 'msie' )   > -1;

      if ( ( is_webkit || is_opera || is_ie ) && document.getElementById && window.addEventListener ) {
        window.addEventListener( 'hashchange', function() {
          var element = document.getElementById( location.hash.substring( 1 ) );
          if ( element ) {
            if ( ! /^(?:a|select|input|button|textarea)$/i.test( element.tagName ) )
              element.tabIndex = -1;
            element.focus();
          }
        }, false );
      }

    };

    /**
     * Things to do when the page is loaded (this function fires autmoatically)
     */
    (exports.Init = function(){
      AO.Spin.LogoSwap();
      AO.Spin.NavHover();
      AO.Spin.ToggleOpen();
      AO.Spin.SkipLinkFocusFix();
    })();

  });

});
