(function () {

  'use strict';

  angular.module('BrandSafetyApp', [])
  .controller('BrandSafetyController', ['$scope', '$log', '$http', '$timeout', '$interval',
    function($scope, $log, $http, $timeout, $interval) {

    $scope.submitButtonText = 'Submit';
    $scope.loading = false;    
    $scope.urlerror = false;    
    $scope.showResultPanel = false;
    var default_info = 'Spent 0 seconds';
    $scope.checkInterval = default_info;
    var terminate = false;
    $scope.getResults = function() {

      $log.log('test');

      // get the URL from the input
      var userInput = $scope.url;
      
      $scope.showResultPanel = true;
      $scope.results = null;
      $scope.loading = true;
      $scope.submitButtonText = 'Analyzing...';
      $scope.urlerror = false;
      
      var index = 0;
//      $scope.checkInterval = index.toString();
      var promise = $interval(callAtinterval, 1000);
      
      $http({method : 'POST', url: '/predict', data : {'website' : userInput}})
      .then(function successCallback(response){
    	  $log.log(results);
    	  $interval.cancel(promise);
    	  $timeout(callAtTimeout, 500);
      }, function errorCallback(response){
    	  $log.log(response);
      });
    $scope.checkInterval = default_info;
      function callAtTimeout(){    	  
    	  getBrandSafety(userInput, true);
      }
      
      function callAtinterval() {
    	  index +=1;
    	  $scope.checkInterval = "Spent " + index.toString() + " seconds";
    	  if(index % 2 ==0){
    		  getBrandSafety(userInput, false);
    	  }      	
      }
      
    };
    
    

    function getBrandSafety(userInput, reset) {

      var timeout = '';

      var poller = function() {
        // fire another request
        $http({method : 'POST', url: '/result', data:{'web' : userInput}})
        .then(function successCallback(response){
        	  $scope.loading = !reset;
              $scope.submitButtonText = reset ? "Submit" : "Analyzing";
              $scope.results = null;
              $scope.results = response.data;
              $scope.urlerror = false;
        }, function errorCallback(response){
      	  $log.log(response);
        }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            
          );
      };

      poller();

    }

  }])

}());