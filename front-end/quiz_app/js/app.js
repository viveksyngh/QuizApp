'use strict';
var app = angular.module('quiz_app', ['ngRoute', 'ngStorage']);

var mainUrl = "http://localhost:8000/#/"
var apiHome = "http://localhost:8080"
// app.run(function($rootScope){
//     $rootScope = {};
// });
	// configure our routes
    app.config(function($routeProvider) {
        $routeProvider

            // route for the home page
            .when('/', {
                templateUrl : 'partials/home.html',
                controller  : 'mainController',
                controllerAs: 'mainCtrl'
            })

            // route for the about page
            .when('/login', {
                templateUrl : 'partials/login.html',
                controller  : 'LoginController',
                controllerAs: 'loginCtrl'
            })

            // route for the contact page
            .when('/register', {
                templateUrl : 'partials/registration.html',
                controller  : 'registerController',
                controllerAs: 'regCtrl'
            })
            .when('/question', {
                templateUrl: 'partials/questions.html',
                controller: 'questionController',
                controllerAs: 'quesCtrl'
            })
            .when('/votes', {
                templateUrl: 'partials/votes.html',
                controller: 'voteController',
                controllerAs: 'voteCtrl'
            })
            .when('/vote/:question_id', {
                templateUrl: 'partials/voting.html',
                controller: 'votingController',
                controllerAs: 'votingCtrl'
            })
            .when('/logout', {
                templateUrl: 'partials/logout.html',
                controller: 'logoutController',
                controllerAs: 'logoutCtrl'
            })
            .otherwise({
                redirectTo: '/'
            })
    });

    // create the controller and inject Angular's $scope
    app.controller('mainController', function($scope, $http, $location, $localStorage) {

        if(!($localStorage.cid && $localStorage.token)) {
            $location.path("/login");
        }

         $scope.showOptionFrom = false;
         $scope.showQuestionForm = true;
         $scope.showQuestionText = false;
         $scope.showOptionList = false;
         $scope.questionText = '';
         $scope.optionList = [];
         $scope.showCreateButton = false;
         $scope.confirmationBox = false;
         $scope.questionLink = '';
        
        this.addQuestion = function(question) {
                $scope.questionText = question;
                $scope.showOptionFrom = true;
                $scope.showQuestionForm = false;
                $scope.showQuestionText = true;
        };

        this.addOption = function(option) {
            if( $scope.showOptionList === false) {
                $scope.showOptionList = true;
            }
            $scope.optionList.push(option);
            $scope.optionText = '';

            if($scope.showCreateButton === false) {
                if($scope.optionList.length > 0) {
                    $scope.showCreateButton = true;
                }
            }
        }

        this.createQuestion = function() {
            
            console.log($scope.questionText);
            console.log($scope.optionList);

            $http({
                method: 'POST',
                url: apiHome + '/quiz/v1/questions/',
                data: 'cid=' + $localStorage.cid + 
                      '&token=' + $localStorage.token + 
                      '&question_text=' + $scope.questionText + 
                      '&options=' + JSON.stringify($scope.optionList),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    console.log("Success");
                    $scope.success = true;
                    $scope.message = response.data.message;
                    $scope.showOptionFrom = false;
                    $scope.showQuestionForm = false;
                    $scope.showQuestionText = false;
                    $scope.showOptionList = false;
                    $scope.showCreateButton = false;
                    $scope.confirmationBox = true;
                    $scope.questionLink = mainUrl + "vote/" + response.data.result.question_id;
                    $location.path("/");

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    if(response.status == '401') {
                        
                        delete $localStorage.cid;
                        delete $localStorage.token;
                        $location.path("/login");
                    }
                    $scope.message = response.data.message;
                 });

        };

    });

    app.controller('questionController', function($scope, $http, $location, $localStorage){

        $scope.questions = [];
        this.questions = function() {            
            $http({
                method: 'GET',
                url: apiHome + '/quiz/v1/questions/?' + 
                     'cid=' + $localStorage.cid + '&token=' + $localStorage.token,
                data: {},
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    console.log("Success");
                    $scope.success = true;
                    $scope.message = response.data.message;
                    var qs = response.data.result.questions;
                    for(var key in qs) {
                        if(qs.hasOwnProperty(key)){
                            $scope.questions.push(qs[key]);
                        }
                    }
                    //$scope.questions = response.data.result.questions;
                    console.log( $scope.questions);
                    console.log(response.data);

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    if(response.status == '401') {
                        
                        delete $localStorage.cid;
                        delete $localStorage.token;
                        $location.path("/login");
                    }
                    $scope.message = response.data.message;
                    console.log(response.data);
                 });
            };

        if ($localStorage.cid && $localStorage.token) {
            this.questions();
        }
        else {
             $location.path("/login");
        }


    });

    app.controller('voteController', function($scope, $http, $location, $localStorage) {
        
        $scope.votes = [];
        
        this.getVotes = function() {            
            $http({
                method: 'GET',
                url: apiHome + '/quiz/v1/votes/?' + 
                     'cid=' + $localStorage.cid + '&token=' + $localStorage.token,
                data: {},
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    console.log("Success");
                    $scope.success = true;
                    $scope.message = response.data.message;
                    $scope.votes = response.data.result.votes;
                    console.log( $scope.votes);
                    console.log(response.data);

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    if(response.status == '401') {
                        
                        delete $localStorage.cid;
                        delete $localStorage.token;
                        $location.path("/login");
                    }
                    $scope.message = response.data.message;
                    console.log(response.data);
                 });
            };

        if ($localStorage.cid && $localStorage.token) {
            this.getVotes();
        }
        else {
             $location.path("/login");
        }

    });

    app.controller('votingController', function($scope, $http, $location, $localStorage, $routeParams){
        
        $scope.question = {};
        $scope.question_id = $routeParams.question_id;
        $scope.optionSelected = 0;
        console.log($scope.question_id);

        this.getQuestion = function(question_id) {
            $http({
                method: 'GET',
                url: apiHome + '/quiz/v1/questions/' + $scope.question_id + '/?'+
                     'cid=' + $localStorage.cid + '&token=' + $localStorage.token,
                data: {},
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    console.log("Success");
                    $scope.success = true;
                    $scope.error = false;
                    $scope.message = response.data.message;
                    $scope.question = response.data.result.question;
                    console.log(response.data);

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    $scope.success = false;
                    if(response.status == '401') {
                        
                        delete $localStorage.cid;
                        delete $localStorage.token;
                        $localStorage.question_id = $scope.question_id;
                        $location.path("/login");
                    }
                    $scope.message = response.data.message;
                    console.log(response.data);
                 });

            };

        this.voteQuestion = function(option_id) {
            $http({
                method: 'POST',
                url: apiHome + '/quiz/v1/votes/',
                data: 'question_id='+ $scope.question_id +
                      '&option_id='+ option_id +
                      '&cid=' + $localStorage.cid + 
                      '&token=' + $localStorage.token,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    $scope.success = true;
                    $scope.error = false;
                    $scope.message = response.data.message;
                    delete $localStorage.cid;
                    $location.path("/");

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    $scope.success = false;
                    if(response.status == '401') {
                        
                        delete $localStorage.cid;
                        delete $localStorage.token;
                        $location.path("/login");
                    }
                    $scope.message = response.data.message;
                    console.log(response.data);
                 });
        };

        if($localStorage.cid && $localStorage.token) {
            this.getQuestion($scope.question_id);
        }

        else {
            $localStorage.question_id = question_id;
            $location.path('/login');
        }

    });

    app.controller('registerController', function($scope, $http, $location) {
        $scope.message = '';
        $scope.success = false;
        $scope.error = false;

        this.register = function(formData) {
            $http({
                method: 'POST',
                url: apiHome + '/user/v1/register/',
                data: 'first_name=' + formData.first_name + 
                      '&middle_name=' + formData.middle_name + 
                      '&last_name=' + formData.last_name + 
                      '&email_id=' + formData.email_id + 
                      '&mobile_no=' + formData.mobile_no +
                      '&password=' + formData.password,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    console.log("Success");
                    $scope.success = true;
                    $scope.message = response.data.message;
                    $location.path("/login");

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    $scope.message = response.data.message;
                 });
            };
    });

	app.controller('LoginController', function($scope, $http, $location, $rootScope, $localStorage) {
	   

       this.login = function(email_id, password) {

        $scope.message = '';
        $scope.success = false;
        $scope.error = false;
          
            $http({
                method: 'POST',
                url: apiHome + '/user/v1/login/',
                data: 'email_id=' + email_id + 
                    '&password=' + password,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                 },
                }).then(function successCallback(response) {
                    console.log("Success");
                    $scope.success = true;
                    $scope.message = response.data.message;
                    $localStorage.cid = response.data.result.cid;
                    $localStorage.token = response.data.result.token;
                    //console.log($localStorage.cid);
                    //console.log($localStorage.token);
                    if($localStorage.question_id) {
                        $location.path("/vote/" + $localStorage.question_id);
                    }
                    else {
                        console.log("Here");
                        $location.path("/");
                    }

                  }, function errorCallback(response) {
                    console.log("Error");
                    $scope.error = true;
                    $scope.message = response.data.message;
            });
	};
});

    app.controller('logoutController', function($scope, $localStorage, $location) {
            if($localStorage.cid && $localStorage.token) {
                delete $localStorage.cid;
                delete $localStorage.token;
                delete $localStorage.question_id; 
            }
            else {
               $location.path('/login');
            }
    });
