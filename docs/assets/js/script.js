var devicon = angular.module('devicon', ['ngSanitize', 'ngAnimate']);
const DEFAULT_BACKGROUND = "#60be86";

/*
||==============================================================
|| Devicons controller
||==============================================================
*/

devicon.controller('IconListCtrl', function($scope, $http, $compile) {

  // Determination of the latest release tagging
  // which is used for showing in the header of the page
  // as well as for CDN links
  var gitHubPath = 'devicons/devicon';
  var url = 'https://api.github.com/repos/' + gitHubPath + '/tags';

  $scope.latestReleaseTagging = 'master';
  $http.get(url).success(function (data) {
    if(data.length > 0) {
      $scope.latestReleaseTagging = data[0].name;
    }
  }).error(function () {
    console.log('Unable to determine latest release version, fallback to master.')
  });


  var baseUrl = `https://cdn.jsdelivr.net/gh/${gitHubPath}/`

  // Get devicon.json
  $http.get(baseUrl + '/devicon.json').success(function(data) {

    /*
    | Re-format devicon.json
    |-----------------------------------------
    */

    // icons related stuff
    $scope.icons = [];
    $scope.selectedIcon = {};

    // background color related stuff
    // default is the default site background color
    $scope.fontBackground = DEFAULT_BACKGROUND;
    $scope.svgBackground = DEFAULT_BACKGROUND;

    // Loop through devicon.json
    angular.forEach(data, function(devicon, key) {

      // New icon format
      var icon = {
        name: devicon.name,
        svg: devicon.versions.svg,
        font: devicon.versions.font,
        main: ""
      };

      // Loop through devicon.json icons
      for (var i = 0; i < devicon.versions.font.length; i++) {

        // Store all versions that should become main in order
        var mainVersionsArray = [
          "plain",
          "line",
          "original",
          "plain-wordmark",
          "line-wordmark",
          "original-wordmark",
        ];

        // Loop through mainVersionsArray
        for (var j = 0; j < mainVersionsArray.length; j++) {

          // Check if icon version can be "main", if not continue, if yes break the loops
          if (devicon.name + devicon.versions.font[i] == devicon.name + mainVersionsArray[j]) {
            icon.main = devicon.name + "-" + devicon.versions.font[i];
            i = 99999; // break first loop (and second)
          }
        }
      }

      // Push new icon format to $scope.icons
      $scope.icons.push(icon);
    });

    // Select first icon by default in scope
    $scope.selectedIcon = $scope.icons[0];
    $scope.selectedFontIcon = $scope.icons[0].font[0];
    $scope.selectedSvgIcon = $scope.selectSvg($scope.icons[0].svg[0], 0);
    $scope.selectedFontIndex = 0;

    /*------ End of "Re-format devicon.json" ------*/
  });

  /*
  | Change selected icon
  |--------------------------------
  */
  $scope.selectIcon = function(icon) {
    $scope.selectedIcon = icon;
    $scope.selectedFontIcon = icon.font[0];
    $scope.selectedFontIndex = 0;
    $scope.selectedSvgIcon = $scope.selectSvg(icon.svg[0], 0);

    // reset color
    $scope.fontBackground = DEFAULT_BACKGROUND;
    $scope.svgBackground = DEFAULT_BACKGROUND;
  }
  /*---- End of "Change selected icon" ----*/


  /*
  | Change selected icon font version
  |--------------------------------
  */
  $scope.selectFont = function(fontVersion, colored, index) {
    $scope.selectedFontIcon = fontVersion;
    $scope.colored = colored ? true : false;
    $scope.selectedFontIndex = index;
  }
  /*---- End of "Change selected font icon" ----*/

  /*
  | Change selected icon svg version
  |--------------------------------
  */
  $scope.selectSvg = function(svgVersion, index) {

    $http.get(baseUrl + '/icons/' + $scope.selectedIcon.name + '/' + $scope.selectedIcon.name + '-' + svgVersion + '.svg').success(function(data){

      var svgElement = angular.element(data);
      var innerSvgElement = null;

      /**
       * Loop trough svg image to find
       * the actual svg content (not any comments or stuff
       * we don't care for).
       * See https://github.com/devicons/devicon/issues/444#issuecomment-753699913
       */
      for (const [key, value] of Object.entries(svgElement)) {
        /** [object SVGSVGElement] ensures we have the actual svg content */
        if(value.toString() == '[object SVGSVGElement]') {
          innerSvgElement = value;
          break;
        }
      }

      if(innerSvgElement === null) {
        console.error('Could not find content of given SVG.')
      } else {
        var innerSVG            = (innerSvgElement.innerHTML);
        $scope.selectedSvgIcon  = innerSVG;
        $scope.selectedSvgIndex = index;
      }
    });
  }
  /*---- End of "Change selected svg icon" ----*/
});

/*================ End of "Devicons controller" ================*/

/*
||==================================================================
|| Convert icon img to svg
||==================================================================
*/

devicon.directive('imgToSvg', function ($http, $compile) {

  var baseUrl = window.location.href;

  return {
    link : function($scope, $element, $attrs) {

      $attrs.$observe('src', function(val){

        $http.get(baseUrl + val).success(function(data){

          var svg = angular.element(data);
          svg = svg.removeAttr('xmlns');
          svg = svg.addClass('not-colored');
          svg = svg.attr('svg-color', '');
          var $e = $compile(svg)($scope);
          $element.replaceWith($e);
          $element = $e;
        });
      });
    }
  };
});

/*================ End of "Convert icon img to svg" ================*/

/*
||==================================================================
|| Add color to svg when hovering
||==================================================================
*/

devicon.directive('svgColor', function () {

  return {
    link : function($scope, $element, $attrs) {
      $element.on('mouseenter', function(){
        $element.removeClass('not-colored');
      });
      $element.on('mouseleave', function(){
        $element.addClass('not-colored');
      });
    }
  };
});

/*================ End of "Add color to svg when hovering" ================*/

/*
||==================================================================
|| Show all icons on click
||==================================================================
*/

devicon.directive('iconDetails', function ($http, $compile) {

  return {
    template: '<div class="icon"><article class="icon-detail"><div ng-repeat="svg in icon.svg"><img ng-src="/icons/{{icon.name}}/{{icon.name}}-{{svg}}.svg" alt="{{icon.name}}" /></div></article><img ng-src="/icons/{{icon.name}}/{{icon.main}}.svg" alt="{{icon.name}}" img-to-svg /></div>',
    replace: true,
    scope: {
      icon: "="
    },
    compile: function CompilingFunction($templateElement) {
      $element.on('click', function(){
        $templateElement.replaceWith(this.template);
      });
    }
  };
});

/*================ End of "Add color to svg when hovering" ================*/
